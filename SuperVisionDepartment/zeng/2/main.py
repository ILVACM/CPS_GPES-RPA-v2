from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# 创建一个新的PPT
prs = Presentation()

# 添加标题幻灯片
slide_layout = prs.slide_layouts[0]  # 0代表标题幻灯片布局
slide = prs.slides.add_slide(slide_layout)

# 添加标题
title = slide.shapes.title
title.text = "变电三所220kV瑞宝站10kV备自投装置改造"
title.text_frame.paragraphs[0].font.size = Pt(28)
title.text_frame.paragraphs[0].font.bold = True
title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 0, 0)  # 黑色

# 添加副标题
subtitle = slide.shapes.placeholders[1]
subtitle.text = "典型问题图片分析报告"
subtitle.text_frame.paragraphs[0].font.size = Pt(20)
subtitle.text_frame.paragraphs[0].font.color.rgb = RGBColor(64, 64, 64)  # 灰色

# 添加内容幻灯片
slide_layout = prs.slide_layouts[1]  # 1代表标题和内容布局
slide = prs.slides.add_slide(slide_layout)

# 添加标题
title = slide.shapes.title
title.text = "典型问题图片分析"

# 添加内容文本
content = slide.shapes.placeholders[1]
content.text = "本周发现B类问题(8)项，出现较多的典型问题图片如下：\n\n项目名称：变电三所220kV瑞宝站10kV备自投装置改造"

# 设置文本格式
for paragraph in content.text_frame.paragraphs:
    paragraph.font.size = Pt(18)
    paragraph.font.name = '微软雅黑'
    paragraph.space_after = 0

# 添加图片（假设图片路径为"problem_image.jpg"）
# 注意：图片路径需要是实际存在的文件路径
img_path = r"dist\图片1.png"  # 替换为您的实际图片路径

# 计算图片位置和大小（精确控制）
# 在幻灯片中，1英寸 = 914400个EMU
# 例如，将图片放在距离左边2英寸，距离顶部3英寸的位置，宽度为5英寸，高度为3英寸
left = Inches(1)
top = Inches(3)
width = Inches(2)
height = Inches(3)

# 添加图片
pic = slide.shapes.add_picture(img_path, left, top, width=width, height=height)

# 调整图片位置（如果需要微调）
# pic.left = Inches(2.1)  # 向右移动0.1英寸
# pic.top = Inches(3.1)   # 向下移动0.1英寸

# 添加图片说明
caption = slide.shapes.add_textbox(Inches(2), Inches(6.5), Inches(5), Inches(0.5))
text_frame = caption.text_frame
text_frame.text = "图1：未见站班会及每日安全交底记录表 (B36)"
for paragraph in text_frame.paragraphs:
    paragraph.font.size = Pt(12)
    paragraph.font.color.rgb = RGBColor(128, 128, 128)  # 灰色

# 保存PPT
prs.save(r"dist\test.pptx")
print("PPT文件已成功创建：变电三所问题分析报告.pptx")