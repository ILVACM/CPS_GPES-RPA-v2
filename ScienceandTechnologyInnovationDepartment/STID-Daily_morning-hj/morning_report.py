import pandas as pd
import os
import logging
import sys
from datetime import datetime, timedelta

def get_base_dir():
    """获取exe所在目录（打包后）或脚本所在目录（开发时）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

class MorningReport:
    def __init__(self, date_type='today', output_dir=None):
        base_dir = get_base_dir()
        self.log_path = os.path.join(base_dir, "log")
        self.temp_path = os.path.join(base_dir, "temp")
        if output_dir is None:
            self.output_path = os.path.join(base_dir, "输出")
        else:
            self.output_path = output_dir
        for p in [self.log_path, self.temp_path, self.output_path]:
            os.makedirs(p, exist_ok=True)

        self.date_type = date_type
        if date_type == 'yesterday':
            self.today = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            suffix = "前一日"
        else:
            self.today = datetime.now().strftime('%Y-%m-%d')
            suffix = "今日"

        self._init_logger()

        self.risk_export_file = f"风险表_{self.today}_{suffix}.xlsx"
        self.work_export_file = f"作业表_{self.today}_{suffix}.xlsx"
        self.daily_export_file = f"早晚报_{self.today}_{suffix}.xlsx"

        self.excluded_types = ["配网搬迁", "配网基建", "线路搬迁", "小型基建", "主网基建"]
        self.risk_levels = ['中风险', '高风险', '中', '高']
        self.company_name = "广州电力工程监理有限公司"

    def _init_logger(self):
        log_file = os.path.join(self.log_path, f"log_{self.today}.txt")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(log_file, encoding='utf-8'), logging.StreamHandler()]
        )
        self.logger = logging.getLogger(__name__)

    def get_count(self, df, column):
        return df[column].value_counts().fillna(0)

    def _print_metric(self, title, count_series):
        self.logger.info(title)
        self.logger.info(f"\n{count_series}")
        total = int(count_series.sum())
        self.logger.info(f"总数：{total}")
        print(f"\n{title}")
        print(count_series)
        print(f"总数：{total}")
        return count_series

    def filter_high_risk(self, df):
        return df[df['风险等级'].isin(self.risk_levels)].copy()

    def sum_int(self, series):
        return int(series.sum())

    def _export_to_excel(self, data, file_path, sheet_name=None, index=False):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if isinstance(data, pd.DataFrame):
            sheet = sheet_name if sheet_name else 'Sheet1'
            data.to_excel(file_path, sheet_name=sheet, index=index)
        elif isinstance(data, dict):
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for sheet, df in data.items():
                    df.to_excel(writer, sheet_name=sheet, index=index)
        else:
            raise TypeError("data必须是DataFrame或dict")

    def save_temp(self, df, filename):
        file_path = os.path.join(self.temp_path, filename)
        self._export_to_excel(df, file_path, sheet_name="Sheet1", index=False)
        self.logger.info(f"中间文件已保存: {file_path}")

    def clean_risk_data(self, df_risk):
        self.logger.info("开始清洗风险表")
        self.save_temp(df_risk, "风险表_原始.xlsx")
        mask = ~df_risk['工程类型'].isin(self.excluded_types)
        df_risk_qujijian = df_risk[mask].copy()
        self.save_temp(df_risk_qujijian, "风险表_去基建.xlsx")
        self.logger.info(f"去基建后剩余 {len(df_risk_qujijian)} 行")
        df_risk_original = df_risk[df_risk['项目类型'] == "主网项目"].copy()
        self.save_temp(df_risk_original, "风险表_主网筛选.xlsx")
        self.logger.info(f"主网筛选后剩余 {len(df_risk_original)} 行")
        df_risk_Sheet1 = df_risk_original.drop_duplicates(subset=['项目名称']).dropna(subset=['项目名称'])
        self.save_temp(df_risk_Sheet1, "风险表_去重去空.xlsx")
        self.logger.info(f"去重去空后剩余 {len(df_risk_Sheet1)} 行")
        return df_risk_original, df_risk_qujijian, df_risk_Sheet1

    def clean_work_data(self, df_work, df_staff):
        self.logger.info("开始清洗作业表")
        self.save_temp(df_work, "作业表_原始.xlsx")
        df_work = df_work[df_work['监理单位名称'].str.contains(self.company_name, na=False)]
        self.save_temp(df_work, "作业表_公司筛选.xlsx")
        self.logger.info(f"公司筛选后剩余 {len(df_work)} 行")
        df_work_Sheet1 = df_work.copy()
        df_work_Sheet1 = df_work_Sheet1.merge(df_staff[['姓名', '部门']], left_on='监理人员姓名', right_on='姓名', how='left')
        df_work_Sheet1.rename(columns={'部门': '总监项目部'}, inplace=True)
        self.save_temp(df_work_Sheet1, "作业表_匹配项目部.xlsx")
        matched = df_work_Sheet1['总监项目部'].notna().sum()
        self.logger.info(f"项目部匹配成功率: {matched}/{len(df_work_Sheet1)} ({matched/len(df_work_Sheet1):.1%})")
        df_work_quchong = df_work_Sheet1.drop_duplicates(subset=['项目名称']).dropna(subset=['项目名称'])
        self.save_temp(df_work_quchong, "作业表_去重.xlsx")
        self.logger.info(f"项目去重后剩余 {len(df_work_quchong)} 行")
        df_work_quchong2 = self.filter_high_risk(df_work_Sheet1).drop_duplicates(subset=['项目名称']).dropna(subset=['项目名称'])
        self.save_temp(df_work_quchong2, "作业表_中高风险去重.xlsx")
        self.logger.info(f"中高风险去重后剩余 {len(df_work_quchong2)} 行")
        return df_work, df_work_Sheet1, df_work_quchong, df_work_quchong2

    # 基础指标计算
    def _calc_metric_a(self, df_risk_original):
        return self.get_count(df_risk_original, '所属项目部')
    def _calc_metric_b(self, df_risk_Sheet1):
        return self.get_count(df_risk_Sheet1, '所属项目部')
    def _calc_metric_c(self, df_risk):
        return self.get_count(df_risk, '所属项目部')
    def _calc_metric_d(self, df_risk_qujijian):
        return self.get_count(df_risk_qujijian, '所属项目部')
    def _calc_metric_e(self, df_work_quchong):
        return self.get_count(df_work_quchong, '总监项目部')
    def _calc_metric_f(self, df_risk):
        if '已到位人员' in df_risk.columns:
            arrived_risk = df_risk[df_risk['已到位人员'].notna() & (df_risk['已到位人员'] != '')]
            f = self.get_count(arrived_risk, '所属项目部')
            self.logger.info("指标 f（晚报-项目到位数）已按'已到位人员'非空统计")
        else:
            self.logger.warning("风险表中无'已到位人员'列，指标 f 将使用全量数据")
            f = self.get_count(df_risk, '所属项目部')
        return f

    def calculate_base_metrics(self, df_risk_original, df_risk_Sheet1, df_risk, df_risk_qujijian, df_work_quchong):
        a = self._print_metric("🔹 a. 【主网项目 - 监理宝原表（主网）】", self._calc_metric_a(df_risk_original))
        b = self._print_metric("🔹 b. 【主网项目 - 主网项目去重】", self._calc_metric_b(df_risk_Sheet1))
        c = self._print_metric("🔹 c. 【上报开工项目数】-监理宝原表", self._calc_metric_c(df_risk))
        d = self._print_metric("🔹 d. 【开工项目数】-去基建", self._calc_metric_d(df_risk_qujijian))
        e = self._print_metric("🔹 e. 【实名制去重】-按总监项目部", self._calc_metric_e(df_work_quchong))
        f = self._print_metric("🔹 f. 【晚报-项目到位数】", self._calc_metric_f(df_risk))
        return a, b, c, d, e, f

    # 高级指标计算
    def _calc_g(self, df_risk_qujijian, df_work_quchong2):
        rh1 = self.filter_high_risk(df_risk_qujijian)
        rh1_dept = self.get_count(rh1, '所属项目部')
        wh1 = self.filter_high_risk(df_work_quchong2)
        wh1_dept = self.get_count(wh1, '总监项目部')
        total = rh1_dept.add(wh1_dept, fill_value=0)
        self.logger.info(f"g. 中高风险(1) = {self.sum_int(rh1_dept)} + {self.sum_int(wh1_dept)} = {self.sum_int(total)}")
        print("\n🔹 g. 中高风险(1) = 去基建风险表中高 + 作业表中高（去重）")
        print(f"✅ 总计：{self.sum_int(rh1_dept)} + {self.sum_int(wh1_dept)} = {self.sum_int(total)}")
        return total, rh1_dept, wh1_dept

    def _calc_h(self, df_risk):
        report_high = self.filter_high_risk(df_risk)
        h_total = self.sum_int(self.get_count(report_high, '所属项目部'))
        self.logger.info(f"h. 上报（中高）：{h_total}")
        print("\n🔹 h. 上报（中高）：全量风险表中高风险项目数")
        print(f"✅ 总计：{h_total}")
        return h_total

    def _calc_i(self, df_work):
        i_total = len(df_work)
        self.logger.info(f"i. 作业计划总数：{i_total}")
        print("\n🔹 i. 实名制系统 - 作业计划总数")
        print(f"✅ 总计：{i_total}")
        return i_total

    def _calc_j(self, df_work_Sheet1, i_total):
        arrive = int(df_work_Sheet1['基建人员考勤人数'].sum() if '基建人员考勤人数' in df_work_Sheet1.columns else 0)
        not_arrive = max(i_total - arrive, 0)
        self.logger.info(f"j. 已到位：{arrive}，未到位：{not_arrive}")
        print("\n🔹 j. 实名制到位情况")
        print(f"✅ 已到位：{arrive} | 未到位：{not_arrive}")
        return arrive, not_arrive

    def _calc_k(self, df_work_Sheet1):
        wh2 = self.filter_high_risk(df_work_Sheet1)
        wh2_sum = self.sum_int(self.get_count(wh2, '总监项目部'))
        self.logger.info(f"k. 中高风险(2)应到/实到：{wh2_sum}")
        print("\n🔹 k. 中高风险(2)应到/实到")
        print(f"✅ 应到：{wh2_sum} | 实到：{wh2_sum}")
        return wh2_sum, wh2

    def _calc_l(self, df_risk):
        plan_arrive = df_risk[df_risk['是否计划到达现场'] == '是']
        l_total = self.sum_int(self.get_count(plan_arrive, '所属项目部'))
        self.logger.info(f"l. 计划到位(是)：{l_total}")
        print("\n🔹 l. 计划到位(是)")
        print(f"✅ 总计：{l_total}")
        return l_total

    def _calc_m(self, rh1_dept, wh2):
        rh3_dept = rh1_dept
        wh3_dept = self.get_count(wh2, '总监项目部')
        total3 = rh3_dept.add(wh3_dept, fill_value=0)
        self.logger.info(f"m. 中高风险(3)：{self.sum_int(rh3_dept)} + {self.sum_int(wh3_dept)} = {self.sum_int(total3)}")
        print("\n🔹 m. 中高风险(3) (中高风险作业计划)")
        print(f"✅ 总计：{self.sum_int(rh3_dept)} + {self.sum_int(wh3_dept)} = {self.sum_int(total3)}")
        return total3, rh3_dept, wh3_dept

    def calculate_advanced_metrics(self, df_risk_qujijian, df_risk, df_work, df_work_Sheet1, df_work_quchong2):
        total1, rh1_dept, wh1_dept = self._calc_g(df_risk_qujijian, df_work_quchong2)
        self._calc_h(df_risk)
        i_total = self._calc_i(df_work)
        self._calc_j(df_work_Sheet1, i_total)
        wh2_sum, wh2 = self._calc_k(df_work_Sheet1)
        self._calc_l(df_risk)
        total3, rh3_dept, wh3_dept = self._calc_m(rh1_dept, wh2)
        return total1, total3, wh3_dept, rh3_dept

    # 导出准备
    def _prepare_risk_table(self, df_risk_qujijian):
        risk_cols = ['项目名称', '风险等级', '所属项目部', '计划到位人员', '施工内容']
        df = self.filter_high_risk(df_risk_qujijian)[risk_cols]
        return df

    def _prepare_work_table(self, df_work_Sheet1):
        work_cols = ['项目名称', '计划编号', '风险等级', '项目/工作单位', '监理人员姓名']
        df = self.filter_high_risk(df_work_Sheet1).copy()
        df.insert(0, '排序', df['风险等级'].map({'高风险': 0, '高': 0, '中风险': 1, '中': 1}))
        df = df.sort_values('排序').drop(columns=['排序'])
        return df[work_cols]

    def _prepare_daily_sheets(self, a, b, c, d, e, f):
        return {
            'a_主网原表': a.reset_index().rename(columns={'index': '所属项目部', 0: '数量'}),
            'b_主网去重': b.reset_index().rename(columns={'index': '所属项目部', 0: '数量'}),
            'c_上报开工': c.reset_index().rename(columns={'index': '所属项目部', 0: '数量'}),
            'd_去基建': d.reset_index().rename(columns={'index': '所属项目部', 0: '数量'}),
            'e_实名制去重': e.reset_index().rename(columns={'index': '总监项目部', 0: '数量'}),
            'f_晚报到位': f.reset_index().rename(columns={'index': '所属项目部', 0: '数量'})
        }

    def export_all_excel(self, df_risk_qujijian, df_work_Sheet1, a, b, c, d, e, f):
        risk_df = self._prepare_risk_table(df_risk_qujijian)
        risk_path = os.path.join(self.output_path, self.risk_export_file)
        self._export_to_excel(risk_df, risk_path, sheet_name="Sheet1", index=False)
        self.logger.info(f"风险表已导出: {risk_path}")

        work_df = self._prepare_work_table(df_work_Sheet1)
        work_path = os.path.join(self.output_path, self.work_export_file)
        self._export_to_excel(work_df, work_path, sheet_name="Sheet1", index=False)
        self.logger.info(f"作业表已导出: {work_path}")

        sheets = self._prepare_daily_sheets(a, b, c, d, e, f)
        daily_path = os.path.join(self.output_path, self.daily_export_file)
        self._export_to_excel(sheets, daily_path, index=False)
        self.logger.info(f"早晚报已导出: {daily_path}")
        print(f"✅ 3个Excel表格已全部导出到: {self.output_path}")

    def print_final_summary(self, total1, total3, wh3_dept, rh3_dept):
        summary = f"{self.today}中高风险施工项目{self.sum_int(total1)}项，作业计划{self.sum_int(total3)}项，智慧工程{self.sum_int(wh3_dept)}项，监理宝{self.sum_int(rh3_dept)}项。"
        self.logger.info(f"总结文案: {summary}")
        print("\n✅ 中高风险作业计划")
        print(summary)

    def process_with_files(self, risk_file, work_file, staff_file):
        try:
            self.logger.info("========== 早报系统开始运行（指定文件） ==========")
            df_risk = pd.read_excel(risk_file)
            df_work = pd.read_excel(work_file)
            df_staff = pd.read_excel(staff_file)
            self.logger.info(f"成功读取风险表: {os.path.basename(risk_file)}")
            self.logger.info(f"成功读取作业表: {os.path.basename(work_file)}")
            self.logger.info(f"成功读取人员表: {os.path.basename(staff_file)}")

            risk_original, risk_qujijian, risk_sheet1 = self.clean_risk_data(df_risk)
            work_filtered, work_matched, work_dedup, work_dedup_high = self.clean_work_data(df_work, df_staff)

            a, b, c, d, e, f = self.calculate_base_metrics(
                risk_original, risk_sheet1, df_risk, risk_qujijian, work_dedup
            )
            self.export_all_excel(risk_qujijian, work_matched, a, b, c, d, e, f)

            total1, total3, wh3_dept, rh3_dept = self.calculate_advanced_metrics(
                risk_qujijian, df_risk, work_filtered, work_matched, work_dedup_high
            )
            self.print_final_summary(total1, total3, wh3_dept, rh3_dept)

            self.logger.info("========== 早报处理成功 ==========")
            return True
        except Exception as e:
            self.logger.exception(f"早报处理失败: {e}")
            raise