import os
import pandas as pd
from datetime import datetime
from morning_report import MorningReport

class EveningReport(MorningReport):
    def __init__(self, output_dir=None):
        super().__init__(date_type='today', output_dir=output_dir)
        self.today = datetime.now().strftime('%Y-%m-%d')
        # 以下属性仅用于兼容，实际文件路径由参数传递
        self.violation_file = "履职表单督查导出（无图）.xlsx"
        self.recorder_file = "监理见证记录仪日数据汇总.xlsx"
        self.ignore_recorder_file = "./ignore_recorder.txt"

    def _calc_evening_metrics(self, df_risk, df_risk_qujijian,
                              risk_original, risk_sheet1,
                              work_filtered, work_matched,
                              work_dedup, work_dedup_high):
        # 基础指标 a~f
        a = self._calc_metric_a(risk_original)
        b = self._calc_metric_b(risk_sheet1)
        c = self._calc_metric_c(df_risk)
        d = self._calc_metric_d(df_risk_qujijian)
        e = self._calc_metric_e(work_dedup)
        f = self._calc_metric_f(df_risk)

        # 高级指标 g~k
        total1, _, _ = self._calc_g(df_risk_qujijian, work_dedup_high)
        h_total = self._calc_h(df_risk)
        i_total = self._calc_i(work_filtered)
        arrive, not_arrive = self._calc_j(work_matched, i_total)
        k_total, _ = self._calc_k(work_matched)

        return a, b, c, d, e, f, total1, h_total, i_total, arrive, not_arrive, k_total

    def _print_evening_metrics(self, a, b, c, d, e, f,
                               total1, h_total, i_total, arrive, not_arrive, k_total):
        self._print_metric("🔹 晚报 a. 主网项目 - 监理宝原表", a)
        self._print_metric("🔹 晚报 b. 主网项目去重", b)
        self._print_metric("🔹 晚报 c. 上报开工项目数", c)
        self._print_metric("🔹 晚报 d. 开工项目数 - 去基建", d)
        self._print_metric("🔹 晚报 e. 实名制去重数", e)
        self._print_metric("🔹 晚报 f. 项目到位数", f)

        self.logger.info(f"🔹 晚报 g. 中高风险(1) 总计: {self.sum_int(total1)}")
        print(f"\n🔹 晚报 g. 中高风险(1) = 去基建风险表中高 + 作业表中高（去重）")
        print(f"✅ 总计：{self.sum_int(total1)}")

        self.logger.info(f"🔹 晚报 h. 上报(中高): {h_total}")
        print(f"\n🔹 晚报 h. 上报(中高)：全量风险表中高风险项目数")
        print(f"✅ 总计：{h_total}")

        self.logger.info(f"🔹 晚报 i. 作业计划总数: {i_total}")
        print(f"\n🔹 晚报 i. 实名制系统 - 作业计划总数")
        print(f"✅ 总计：{i_total}")

        self.logger.info(f"🔹 晚报 j. 已到位: {arrive}, 未到位: {not_arrive}")
        print(f"\n🔹 晚报 j. 实名制到位情况")
        print(f"✅ 已到位：{arrive} | 未到位：{not_arrive}")

        self.logger.info(f"🔹 晚报 k. 中高风险(2) 应到/实到: {k_total}")
        print(f"\n🔹 晚报 k. 中高风险(2)应到/实到")
        print(f"✅ 应到：{k_total} | 实到：{k_total}")

    def process_with_files(self, risk_file, work_file, staff_file, violation_file=None, recorder_file=None):
        try:
            self.logger.info("========== 晚报系统开始运行（指定文件，当日16时） ==========")
            df_risk = pd.read_excel(risk_file)
            df_work = pd.read_excel(work_file)
            df_staff = pd.read_excel(staff_file)
            self.logger.info(f"成功读取风险表: {os.path.basename(risk_file)}")
            self.logger.info(f"成功读取作业表: {os.path.basename(work_file)}")
            self.logger.info(f"成功读取人员表: {os.path.basename(staff_file)}")

            risk_original, risk_qujijian, risk_sheet1 = self.clean_risk_data(df_risk)
            work_filtered, work_matched, work_dedup, work_dedup_high = self.clean_work_data(df_work, df_staff)

            (a, b, c, d, e, f,
             total1, h_total, i_total, arrive, not_arrive, k_total) = self._calc_evening_metrics(
                df_risk, risk_qujijian,
                risk_original, risk_sheet1,
                work_filtered, work_matched,
                work_dedup, work_dedup_high
            )

            self._print_evening_metrics(a, b, c, d, e, f,
                                        total1, h_total, i_total, arrive, not_arrive, k_total)

            self._export_evening_excel(risk_qujijian, work_matched, a, b, c, d, e, f)

            if violation_file and os.path.exists(violation_file):
                self.export_violation_data(violation_file)
            else:
                self.logger.warning("未提供违章闭环文件或文件不存在，跳过导出")

            if recorder_file and os.path.exists(recorder_file):
                self.export_recorder_usage(recorder_file)
            else:
                self.logger.warning("未提供记录仪文件或文件不存在，跳过导出")

            summary = (f"{self.today} 16时晚报统计：中高风险施工项目{self.sum_int(total1)}项，"
                       f"作业计划{i_total}项，已到位{arrive}人，未到位{not_arrive}人。")
            self.logger.info(summary)
            print("\n✅ 晚报处理完成")
            print(summary)

            self.logger.info("========== 晚报处理成功 ==========")
            return True

        except Exception as e:
            self.logger.exception(f"晚报处理失败: {e}")
            raise

    def _export_evening_excel(self, df_risk_qujijian, df_work_matched,
                              a, b, c, d, e, f):
        risk_cols = ['项目名称', '风险等级', '所属项目部', '计划到位人员', '施工内容']
        risk_out = self.filter_high_risk(df_risk_qujijian)[risk_cols]
        risk_path = os.path.join(self.output_path, f"风险表_晚报_{self.today}.xlsx")
        self._export_to_excel(risk_out, risk_path, index=False)
        self.logger.info(f"晚报风险表已导出: {risk_path}")

        work_cols = ['项目名称', '计划编号', '风险等级', '项目/工作单位', '监理人员姓名']
        work_high = self.filter_high_risk(df_work_matched).copy()
        work_high.insert(0, '排序', work_high['风险等级'].map({'高风险': 0, '高': 0, '中风险': 1, '中': 1}))
        work_high = work_high.sort_values('排序').drop(columns=['排序'])
        work_path = os.path.join(self.output_path, f"作业表_晚报_{self.today}.xlsx")
        self._export_to_excel(work_high[work_cols], work_path, index=False)
        self.logger.info(f"晚报作业表已导出: {work_path}")

        sheets = {
            'a_主网原表_晚报': a.reset_index().rename(columns={'index': '所属项目部', 0: '数量'}),
            'b_主网去重_晚报': b.reset_index().rename(columns={'index': '所属项目部', 0: '数量'}),
            'c_上报开工_晚报': c.reset_index().rename(columns={'index': '所属项目部', 0: '数量'}),
            'd_去基建_晚报': d.reset_index().rename(columns={'index': '所属项目部', 0: '数量'}),
            'e_实名制去重_晚报': e.reset_index().rename(columns={'index': '总监项目部', 0: '数量'}),
            'f_晚报到位_晚报': f.reset_index().rename(columns={'index': '所属项目部', 0: '数量'})
        }
        daily_path = os.path.join(self.output_path, f"早晚报计数表_晚报_{self.today}.xlsx")
        self._export_to_excel(sheets, daily_path, index=False)
        self.logger.info(f"晚报计数表已导出: {daily_path}")

    def export_violation_data(self, file_path):
        try:
            if not os.path.exists(file_path):
                self.logger.warning(f"违章闭环文件不存在: {file_path}")
                return
            df_vio = pd.read_excel(file_path)
            required_cols = ['四类问题', '闭环状态']
            if not all(col in df_vio.columns for col in required_cols):
                self.logger.error(f"违章文件缺少必要列: {required_cols}")
                return
            mask = (df_vio['四类问题'].str.contains('杜绝类|严禁类', na=False)) & (df_vio['闭环状态'] == '未闭环')
            df_filtered = df_vio[mask].copy()
            out_cols = ['项目类型', '工程名称', '建设单位', '总包单位', '分包单位',
                        '作业日期', '问题描述项', '作业计划编号', '所属项目部', '检查人', '闭环状态']
            out_cols = [c for c in out_cols if c in df_filtered.columns]
            df_out = df_filtered[out_cols]
            count = len(df_out)
            self.logger.info(f"违章闭环: 杜绝类/严禁类未闭环共 {count} 项")
            out_path = os.path.join(self.output_path, f"违章闭环未闭环_{self.today}.xlsx")
            self._export_to_excel(df_out, out_path, index=False)
            ppt_summary = f"查询{self.today}安全履职表单AB类违章有 {count} 项未闭环。"
            self.logger.info(ppt_summary)
            print(ppt_summary)
        except Exception as e:
            self.logger.error(f"处理违章闭环数据失败: {e}")

    def export_recorder_usage(self, file_path):
        try:
            if not os.path.exists(file_path):
                self.logger.warning(f"记录仪文件不存在: {file_path}")
                return
            df_rec = pd.read_excel(file_path)
            if '绑定时长' in df_rec.columns:
                def parse_minutes(t):
                    if pd.isna(t) or t == '':
                        return 0
                    if isinstance(t, (int, float)):
                        return t
                    s = str(t)
                    if '分钟' in s:
                        return int(s.replace('分钟', ''))
                    return 0
                df_rec['绑定时长_分钟'] = df_rec['绑定时长'].apply(parse_minutes)
                df_rec = df_rec[(df_rec['绑定时长_分钟'] >= 6) | (df_rec['绑定时长_分钟'] == 0)]
            if os.path.exists(self.ignore_recorder_file):
                with open(self.ignore_recorder_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or ',' not in line:
                            continue
                        name, dept = line.split(',', 1)
                        df_rec = df_rec[~((df_rec['绑定人姓名'] == name) &
                                          (df_rec['人员所属项目部'] == dept))]
            if '人员所属项目部' not in df_rec.columns or '绑定人姓名' not in df_rec.columns:
                self.logger.error("记录仪文件缺少必要列: 人员所属项目部 或 绑定人姓名")
                return
            usage = df_rec.groupby('人员所属项目部')['绑定人姓名'].nunique().reset_index()
            usage.columns = ['总监项目部', '使用台数']
            if '持有台数' not in df_rec.columns:
                self.logger.error("记录仪文件缺少必要列: 持有台数")
                return
            holding = df_rec[['人员所属项目部', '持有台数']].drop_duplicates(subset='人员所属项目部')
            holding.columns = ['总监项目部', '持有台数']
            result = usage.merge(holding, on='总监项目部', how='outer').fillna(0)
            result['使用率'] = result.apply(
                lambda row: f"{row['使用台数']/row['持有台数']:.2%}" if row['持有台数'] > 0 else "0.00%",
                axis=1
            )
            out_path = os.path.join(self.output_path, f"监理见证记录仪日数据汇总_{self.today}.xlsx")
            self._export_to_excel(result, out_path, index=False)
            self.logger.info(f"监理见证记录仪日数据汇总已导出: {out_path}")
        except Exception as e:
            self.logger.error(f"处理记录仪数据失败: {e}")