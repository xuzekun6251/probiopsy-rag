# -*- coding: utf-8 -*-
"""Build the Chinese translation of Tung et al., J Med Internet Res 2025;27:e78393,
mirroring the original JMIR layout. Rebuild with: .venv/Scripts/python.exe scripts/build_tung_translation_docx.py"""
import re
from pathlib import Path

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT_DOCX = Path(r"D:\Zcode测试文件夹\前列腺智能体_中文翻译.docx")
FIG = Path(r"D:\Zcode测试文件夹\测试3\outputs\tung_fig1.png")

doc = Document()

# ---------- page setup (A4, JMIR-like margins) ----------
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.0)
sec.top_margin, sec.bottom_margin = Cm(2.2), Cm(2.0)
sec.header_distance, sec.footer_distance = Cm(1.1), Cm(1.0)

st = doc.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
st.paragraph_format.space_after = Pt(6)
st.paragraph_format.line_spacing = 1.15

# ---------- helpers ----------
def para(text=None, size=10.5, bold=False, italic=False, align=None,
         before=0, after=6, color=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    if align is not None:
        p.alignment = align
    if text:
        r = p.add_run(text)
        r.font.size = Pt(size)
        r.bold = bold
        r.italic = italic
        if color:
            r.font.color.rgb = color
    return p

def add_runs(p, parts, size=10.5):
    """parts: list of (text, {bold, italic, sup, size, color})"""
    for text, kw in parts:
        r = p.add_run(text)
        r.font.size = Pt(kw.get("size", size))
        r.bold = kw.get("bold", False)
        r.italic = kw.get("italic", False)
        if kw.get("sup"):
            r.font.superscript = True
        if kw.get("color"):
            r.font.color.rgb = kw["color"]
    return p

def h1(text, before=14):
    para(text, size=14, bold=True, before=before, after=6)

def h2(text, before=10):
    para(text, size=12, bold=True, before=before, after=4)

def labeled(label, text, size=10.5, before=0, after=6):
    p = para(None, before=before, after=after)
    add_runs(p, [(label, {"bold": True}), (text, {})], size=size)
    return p

def sup_split(p, text, size):
    """Render digit runs as superscripts (author/affiliation markers)."""
    for chunk in re.split(r"(\d+)", text):
        if not chunk:
            continue
        if chunk.isdigit():
            add_runs(p, [(chunk, {"sup": True})], size=size)
        else:
            add_runs(p, [(chunk, {})], size=size)

# ---------- running header ----------
hp = sec.header.paragraphs[0]
hp.paragraph_format.tab_stops.add_tab_stop(Cm(17.0), WD_TAB_ALIGNMENT.RIGHT)
hr = hp.add_run("JOURNAL OF MEDICAL INTERNET RESEARCH\tTung et al")
hr.font.size = Pt(9)
pPr = hp._p.get_or_add_pPr()
pbdr = OxmlElement("w:pBdr")
bottom = OxmlElement("w:bottom")
bottom.set(qn("w:val"), "single")
bottom.set(qn("w:sz"), "6")
bottom.set(qn("w:space"), "1")
bottom.set(qn("w:color"), "auto")
pbdr.append(bottom)
pPr.append(pbdr)

# ---------- running footer with PAGE field ----------
fp = sec.footer.paragraphs[0]
fp.paragraph_format.tab_stops.add_tab_stop(Cm(17.0), WD_TAB_ALIGNMENT.RIGHT)
fr = fp.add_run("https://www.jmir.org/2025/1/e78393\tJ Med Internet Res 2025 | vol. 27 | e78393 | p. ")
fr.font.size = Pt(8.5)
fld_begin = OxmlElement("w:fldChar"); fld_begin.set(qn("w:fldCharType"), "begin")
instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = "PAGE"
fld_end = OxmlElement("w:fldChar"); fld_end.set(qn("w:fldCharType"), "end")
r_b = fp.add_run(); r_b.font.size = Pt(8.5); r_b._r.append(fld_begin)
r_i = fp.add_run(); r_i.font.size = Pt(8.5); r_i._r.append(instr)
r_e = fp.add_run(); r_e.font.size = Pt(8.5); r_e._r.append(fld_end)
fr2 = fp.add_run(" (page number not for citation purposes)")
fr2.font.size = Pt(8.5)

# =====================================================================
# title page
# =====================================================================
para("原著（Original Paper）", size=12, bold=True, after=10)

p = para(None, after=12)
add_runs(p, [("检索增强生成大语言模型在与指南一致的前列腺特异性抗原检测中的表现：与低年资临床医师的比较研究",
              {"bold": True, "size": 15})])

AUTHORS = ("Joshua Yi Min Tung1,2, MBBS, MPH; Quan Le1, BEng, MITB; Jinxuan Yao1, BEng, MTech; "
           "Yifei Huang1, BCS, MTech; Daniel Yan Zheng Lim1,3, MBBS, MTech; "
           "Gerald Gui Ren Sng1,4, MBBS, MPH, MMed; Rachel Shu En Lau2, MBBS; "
           "Yu Guang Tan2, MBBS, MCI; Kenneth Chen2, MBBS, MCI; Kae Jack Tay2, MBBS, MMed, MCI; "
           "Jen Hong Tan1, BEng, PhD; John Shyi Peng Yuen2, MBBS, MMed, DPhil; "
           "Christopher Wai Sam Cheng2, MBBS, MMed; Henry Sun Sien Ho2, MBBS, MMed")
p = para(None, after=8)
sup_split(p, AUTHORS, size=10)

AFFILS = [
    "1数据科学与人工智能实验室，新加坡中央医院，新加坡",
    "2泌尿外科，新加坡中央医院，新加坡",
    "3胃肠病学科，新加坡中央医院，新加坡",
    "4内分泌科，新加坡中央医院，新加坡",
]
for a in AFFILS:
    p = para(None, after=2)
    sup_split(p, a, size=9)

para("", after=2)
labeled("通讯作者：\n", "")  # placeholder replaced below
# rebuild the corresponding-author block properly (multi-line)
doc.paragraphs[-1]._p.getparent().remove(doc.paragraphs[-1]._p)
para("通讯作者：", size=10, bold=True, after=2)
for line in ["Joshua Yi Min Tung, MBBS, MPH", "泌尿外科", "新加坡中央医院",
             "Block 4 Level 1, 16 College Road", "Singapore 169854", "Singapore",
             "电话：65 62223322", "电子邮箱：joshua.tung@gmail.com"]:
    para(line, size=10, after=1)

# ---------- abstract ----------
para("摘要", size=14, bold=True, before=12, after=6)
labeled("背景：", "前列腺特异性抗原（prostate-specific antigen, PSA）检测仍是前列腺癌早期发现的基石。通过PSA检测进行前列腺癌筛查的学会指南旨在规范患者诊疗，并常被受训医师、低年资医师或非专科的全科医师用于指导医疗决策。然而，遵循指南是一项耗时且具挑战性的任务，不恰当PSA检测的发生率很高。检索增强生成（retrieval-augmented generation, RAG）是一种通过把大语言模型（large language model, LLM）的回答锚定于可信外部来源来提高其可靠性的方法。")
labeled("目的：", "本研究旨在评估一个以现行欧洲泌尿外科学会（European Association of Urology）和美国泌尿外科学会（American Urological Association）指南为依据的RAG增强LLM系统，考察其相对于低年资临床医师在提供与指南一致的PSA筛查建议方面的有效性。")
labeled("方法：", "研究构建了一系列44个虚构门诊病例场景，以覆盖广泛的临床表现。开发了一条RAG管线，包括一个基于Charlson共病指数（Charlson Comorbidity Index）的预期寿命估算模块，其后是由从欧洲泌尿外科学会和美国泌尿外科学会指南中检索到的摘录所约束的LLM生成建议。5名低年资临床医师需以闭卷和开卷两种形式就相同场景提供PSA检测建议。答案以二分类方式比较准确性，并计算Fleiss κ评估临床医师之间的评分者间一致性。")
labeled("结果：", "RAG-LLM工具在95.5%（210/220）的病例场景中给出了与指南一致的建议；相比之下，低年资临床医师在闭卷形式下正确率为62.3%（137/220），开卷形式下为74.1%（163/220）。两种形式的差异均有统计学意义（闭卷P<.001，开卷P<.001）。临床医师之间的评分者间一致性为一般水平，闭卷和开卷形式的Fleiss κ分别为0.294和0.321。")
labeled("结论：", "使用RAG技术可使LLM把复杂指南整合进日常医疗决策。泌尿外科领域的RAG-LLM工具能够通过为PSA检测提供与指南一致的建议来增强临床决策，有望提高医疗服务的一致性、减轻临床医师的认知负荷，并减少不必要的检查与费用。尽管本研究使用的是受控模拟环境中的合成病例，但其为今后在真实临床环境中的验证奠定了基础。")

para("J Med Internet Res 2025;27:e78393; doi: 10.2196/78393", size=10.5,
     bold=True, italic=True, before=10)
labeled("关键词：", "人工智能；AI；大语言模型；LLM；指南一致性；低年资临床医师", before=4)

# =====================================================================
# Introduction
# =====================================================================
h1("引言")
para("前列腺癌是全球男性中第二常见的确诊癌症，也是男性癌症相关死亡的第五大原因[1]。因此，前列腺癌筛查在初级诊疗和专科诊疗中都是一个常见问题。前列腺特异性抗原（PSA）检测是应用最广的早期发现方法，但在泌尿外科文献中仍存在争议，这主要源于过度诊断和过度治疗带来的危害[2,3]。")
para("通过PSA检测进行前列腺癌筛查的学会指南旨在简化和规范患者诊疗，并常被受训医师、低年资医师或非专科医师用于指导医疗决策。欧洲泌尿外科学会（EAU）[4]和美国泌尿外科学会（AUA）[5]等多个组织均发布了此类指南，但指南之间存在差异，例如关于是否应提供PSA筛查、合适的目标人群以及筛查间隔的推荐各不相同，给临床决策带来了挑战。此外，还需要考虑其他患者因素，例如需要计算估算预期寿命（因为许多指南不建议对预期寿命不足10年或15年的患者进行PSA筛查），以及需要考虑患者自身偏好，这使问题更加复杂。共同决策是EAU和AUA指南的重要组成部分，尤其是对老年男性或患有多种内科共病的患者而言。")
para("现行EAU-欧洲核医学学会-欧洲放射肿瘤学会-欧洲泌尿生殖放射学会-国际泌尿病理学会-国际老年肿瘤学会指南，以及AUA和泌尿肿瘤学会关于前列腺癌和前列腺癌早期发现的指南，分别长达239页和47页。因此，无论是初级诊疗环境中的非专科医师，还是门诊环境中时间普遍紧张的专科医师，作出恰当决策并遵循指南都是一项耗时且艰巨的任务。既往研究显示指南依从率较低，例如一项纳入32,306名男性的队列研究显示，>80岁人群中有40%接受了不恰当的PSA筛查[6]。")
para("一个潜在的解决方案是使用人工智能（artificial intelligence, AI）来解析指南并给出恰当的推荐。大语言模型（LLM）是一类在海量文本数据上训练的AI，能够处理非结构化文本输入并生成恰当的回答，因此可应用于医疗领域，例如患者沟通、教育和临床风险分层[7]。然而，OpenAI开发的GPT系列模型等通用LLM并非专为医疗用途设计，可能产生不准确或具有误导性的信息。它们的知识存在截止时间，取决于底层训练数据的新近程度，例如OpenAI GPT-4模型为2022年1月。为解决这些局限，研究者开发了检索增强生成（RAG）技术，以提高LLM的准确性。RAG引导LLM在回答给定场景时参考一个额外的经整理的信息数据库，例如一套指南。通过利用数据库中的相关信息来锚定回答，LLM可以克服其固有的知识截止局限，产生幻觉更少的回答[8-10]。")
para("因此，本研究旨在评估一个以EAU和AUA前列腺癌筛查指南为依据的RAG增强LLM的准确性。")

# =====================================================================
# Methods
# =====================================================================
h1("方法")
h2("伦理考量")
para("本研究在模拟环境中开展，仅使用虚构患者数据。由于虚构数据的使用不属于当地《人体生物医学研究法》（Human Biomedical Research Act）的监管范围，因此无需伦理批准。")
h2("病例场景的构建")
para("研究构建了一系列共44个虚构病例场景，以反映门诊环境中的一系列临床表现。这些自由文本场景包含虚构患者的个人资料，如年龄、内科共病、有无泌尿系统症状（如血尿或下尿路症状，如适用）以及既往PSA读数（如适用）。场景由一名具有8年临床经验的泌尿外科专科培训医师（fellow）撰写，并由2名临床经验均超过20年的泌尿外科顾问医师监督审核。")
h2("RAG增强大语言模型的开发")
para("我们按照医疗服务提供者给出PSA检测建议的方式，开发了一条处理病例场景的自动化管线。流程示意图如图1所示。")

# figure caption above the diagram (as in the original)
p = para(None, after=4)
add_runs(p, [("图1. ", {"bold": True}),
             ("用于前列腺特异性抗原（PSA）检测推荐的检索增强生成赋能大语言模型管线的流程示意图。AUA：美国泌尿外科学会；CCI：Charlson共病指数；CHF：充血性心力衰竭；EAU：欧洲泌尿外科学会。", {})])
pic_p = doc.add_paragraph()
pic_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
pic_p.paragraph_format.space_after = Pt(10)
pic_p.add_run().add_picture(str(FIG), width=Cm(15.0))

para("该管线的关键组成部分包括一个基于LLM的计算器，用于从病例场景中提取相关患者信息（年龄和共病），计算Charlson共病指数（CCI），从而估算预期10年寿命。预期寿命不足10年的患者不被建议进行PSA筛查[4,5]，管线不允许此类病例场景继续处理。同样，患者年龄>72岁的场景也不被允许继续处理。CCI计算器的更多技术细节见多媒体附录1[3-5,11,12]。")
para("对于根据CCI评分预期寿命至少为10年的患者，使用RAG增强LLM基于给定病例场景提供建议。与未经特定医学领域信息训练的标准“现成”（off-the-shelf）LLM相比，RAG允许LLM参考一组固定的资料，例如本研究中相关的EAU和AUA学会指南。以此方式用情境化信息增强的语言模型可以克服其固有的知识缺陷，并通过把回答约束在所提供的信息之内来减少幻觉。")
para("由于AUA和EAU指南偶尔会给出互不重叠的不同推荐，因此先分别依据每套指南生成答案，再将二者合并产生最终推荐。")
para("RAG增强LLM的更多技术细节见多媒体附录1[3-5,11,12]，其中包括对应用于优化性能的现代RAG技术的说明，例如改进相关信息检索的上下文过滤，以及先进的提示方法（思维链推理[13]、把回答约束于检索到的信息、提供示例输出结构和使用专家临床医师角色设定）。完整的RAG提示词见多媒体附录1[3-5,11,12]。")

h2("相关软件")
para("RAG原型使用Python（3.10版；Python Software Foundation）开发。向量数据库的构建流程为：使用Unstructured API摄取PDF文档，使用OpenAI API生成文本嵌入，并使用Qdrant作为向量数据库。在LLM调用方面，管线中的不同组件分别使用了OpenAI和Anthropic API。我们同时使用LlamaIndex和Langchain进行编排：LlamaIndex负责检索增强生成组件的检索，Langchain则用于结构化数据提取和管线组件之间的连接。")

h2("答案的生成与评分")
para("5名低年资临床医师负责就每个病例场景提供PSA检测建议，包括1名第一年医学官（medical officer）、1名第二年家庭医学住院医师、2名第二年泌尿外科住院医师和1名第三年泌尿外科住院医师。每位临床医师先以“闭卷”形式完成任务，随后以“开卷”形式完成；开卷时允许其查阅自选的相关资料（如指南或教科书）。两种形式各自的完成用时均有记录。")
para("RAG-LLM工具同样接受同一组虚构病例场景，并被要求就PSA检测提供建议。我们进行了5次运行，以评估LLM输出的一致性。答案由研究团队按二分类方式（正确或不正确）评分；凡与EAU或AUA任一指南一致的回答即标记为正确。")

h2("统计分析")
para("定量数据的统计分析使用SPSS（26.0版；IBM Corp）完成。RAG-LLM工具与人类对照者的回答采用Student双侧t检验进行比较。评分者间一致性采用Fleiss κ计算。")

# =====================================================================
# Results
# =====================================================================
h1("结果")
para("RAG-LLM工具在95.5%（210/220）的病例场景中给出了与指南一致的建议；相比之下，低年资临床医师在闭卷形式下正确率为62.3%（137/220），开卷形式下为74.1%（163/220）。闭卷（P<.001）和开卷（P<.001）两种形式的差异均有统计学意义。")
para("病例分为筛查类（20/44，45.5%）和随访类（24/44，54.5%）。RAG-LLM工具在1例筛查病例中给出了不正确的推荐：在全部5次运行中，它均未能为一名符合筛查推荐条件的患者建议PSA检测。相比之下，低年资临床医师在闭卷形式下遗漏了16/100（16%）的检测，开卷形式下遗漏了11/100（11%）；他们还在闭卷形式下多做了14/100（14%）不必要的PSA检测，开卷形式下为10/100（10%）。在随访病例中，RAG-LLM工具在1例中给出了不正确的推荐：在全部5次运行中，它均错误地建议一名PSA读数正常的患者重复PSA检测。相比之下，低年资临床医师在闭卷形式下开具了29/120（24.2%）的不必要检测，开卷形式下为23/120（19.2%）；闭卷和开卷形式下分别遗漏了24/120（20%）和13/120（10.8%）的检测。总体而言，RAG-LLM工具比低年资临床医师少推荐了71例（5 vs 76，93.4%）不必要的PSA检测，少遗漏了59例（5 vs 64，92.2%）本应提供的PSA检测。")
para("结果进一步按以下病例类别进行分析：（1）建议进行PSA筛查；（2）不建议进行PSA筛查；（3）PSA读数正常者的随访；（4）PSA读数升高的处理或随访；以及（5）其他，包括可能因并发泌尿道感染导致的PSA读数假性升高、共病严重且进一步或重复检测不太可能获益的患者的PSA读数升高，以及直肠指检异常患者的PSA读数正常。结果详见表1。")

# ---------- Table 1 ----------
p = para(None, before=8, after=4)
add_runs(p, [("表1. ", {"bold": True}),
             ("检索增强生成-大语言模型（RAG-LLM）与低年资临床医师前列腺特异性抗原（PSA）检测推荐的准确性与错误分布。", {})])

rows, cols = 25, 9
tbl = doc.add_table(rows=rows, cols=cols)
tbl.style = "Table Grid"
tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl.autofit = False

widths = [Cm(3.0), Cm(1.7), Cm(1.7), Cm(1.7), Cm(1.7), Cm(1.7), Cm(1.7), Cm(1.9), Cm(1.4)]

def set_cell(cell, parts, align=WD_ALIGN_PARAGRAPH.CENTER, size=9):
    cell.text = ""
    cp = cell.paragraphs[0]
    cp.paragraph_format.space_after = Pt(2)
    cp.paragraph_format.space_before = Pt(1)
    cp.alignment = align
    add_runs(cp, parts, size=size)

def merge_group(row_idx, label):
    c = tbl.cell(row_idx, 0)
    for j in range(1, cols):
        c = c.merge(tbl.cell(row_idx, j))
    set_cell(c, [(label, {"bold": True})], align=WD_ALIGN_PARAGRAPH.LEFT)

# header (two rows with merges)
set_cell(tbl.cell(0, 0).merge(tbl.cell(1, 0)), [("分组与类别", {"bold": True}), ("a", {"bold": True, "sup": True})])
set_cell(tbl.cell(0, 1).merge(tbl.cell(0, 3)), [("不必要的检测，n (%)", {"bold": True})])
set_cell(tbl.cell(0, 4).merge(tbl.cell(0, 6)), [("遗漏的检测，n (%)", {"bold": True})])
set_cell(tbl.cell(0, 7).merge(tbl.cell(1, 7)), [("错误总数，n (%)", {"bold": True})])
set_cell(tbl.cell(0, 8).merge(tbl.cell(1, 8)), [("P值", {"bold": True})])
for j, t in enumerate(["间隔过短", "无需检测", "小计", "间隔过长", "未提供检测", "小计"]):
    set_cell(tbl.cell(1, j + 1), [(t, {"bold": True})])

DATA = [
    (2, "整体（n=220）", None),
    (3, "LLM",            ["5 (2.3)", "0 (0)", "5 (2.3)", "0 (0)", "5 (2.3)", "5 (2.3)", "10 (4.5)", "—b"]),
    (4, "人类，闭卷",      ["11 (5.0)", "32 (14.5)", "43 (19.5)", "26 (11.8)", "14 (6.4)", "40 (18.2)", "83 (37.7)", "<.001"]),
    (5, "人类，开卷",      ["10 (4.5)", "23 (10.5)", "33 (15.0)", "14 (6.4)", "10 (4.5)", "24 (10.9)", "57 (25.9)", "<.001"]),
    (6, "类别1：建议进行PSA筛查（n=55）", None),
    (7, "LLM",            ["0 (0)", "0 (0)", "0 (0)", "0 (0)", "5 (9.1)", "5 (9.1)", "5 (9.1)", "—"]),
    (8, "人类，闭卷",      ["0 (0)", "0 (0)", "0 (0)", "3 (6.7)", "10 (18.2)", "13 (23.6)", "13 (23.6)", ".04"]),
    (9, "人类，开卷",      ["0 (0)", "0 (0)", "0 (0)", "1 (1.8)", "10 (18.2)", "11 (20)", "11 (20)", ".11"]),
    (10, "类别2：不建议进行PSA筛查（n=45）", None),
    (11, "LLM",           ["0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "—"]),
    (12, "人类，闭卷",     ["0 (0)", "14 (31.1)", "14 (31.1)", "3 (6.7)", "0 (0)", "3 (6.7)", "17 (37.8)", "<.001"]),
    (13, "人类，开卷",     ["0 (0)", "10 (22.2)", "10 (22.2)", "0 (0)", "0 (0)", "0 (0)", "10 (22.2)", ".001"]),
    (14, "类别3：PSA读数正常者的随访（n=45）", None),
    (15, "LLM",           ["5 (11.1)", "0 (0)", "5 (11.1)", "0 (0)", "0 (0)", "0 (0)", "5 (11.1)", "—"]),
    (16, "人类，闭卷",     ["8 (17.8)", "8 (17.8)", "16 (35.6)", "0 (0)", "3 (6.7)", "3 (6.7)", "19 (42.2)", ".001"]),
    (17, "人类，开卷",     ["7 (15.6)", "7 (15.6)", "14 (31.1)", "1 (2.2)", "0 (0)", "1 (2.2)", "15 (33.3)", ".01"]),
    (18, "类别4：PSA读数升高（n=40）", None),
    (19, "LLM",           ["0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "—"]),
    (20, "人类，闭卷",     ["0 (0)", "0 (0)", "0 (0)", "20 (50)", "1 (2.5)", "21 (52.5)", "21 (52.5)", "<.001"]),
    (21, "人类，开卷",     ["1 (2.5)", "0 (0)", "1 (2.5)", "12 (30)", "0 (0)", "12 (30)", "13 (28.9)", "<.001"]),
    (22, "类别5：其他（n=35）", None),
    (23, "LLM",           ["0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "0 (0)", "—"]),
    (24, "人类，闭卷",     ["3 (8.6)", "10 (28.6)", "13 (37.1)", "0 (0)", "0 (0)", "0 (0)", "13 (37.1)", "<.001"]),
    (25 - 1, "人类，开卷", ["2 (5.7)", "6 (17.1)", "8 (22.9)", "0 (0)", "0 (0)", "0 (0)", "8 (22.9)", ".002"]),
]
for row in DATA:
    idx, label, vals = row
    if vals is None:
        merge_group(idx, label)
    else:
        set_cell(tbl.cell(idx, 0), [(label, {})], align=WD_ALIGN_PARAGRAPH.LEFT)
        for j, v in enumerate(vals):
            if v == "—b":
                set_cell(tbl.cell(idx, j + 1), [("—", {}), ("b", {"sup": True})])
            else:
                set_cell(tbl.cell(idx, j + 1), [(v, {})])

for r in tbl.rows:
    for j, c in enumerate(r.cells):
        try:
            c.width = widths[j]
        except Exception:
            pass

p = para(None, before=3, after=2)
add_runs(p, [("a", {"sup": True, "size": 8.5}),
             (" 所有百分比计算的分母均为各类别病例数乘以5，因为44个病例场景中的每一个均由5名低年资临床医师独立评估。因此，总体例数显示为n=220，各类别的分母（如类别1的n=55、类别2的n=45等）按同一方法计算。", {"size": 8.5})])
p = para(None, after=8)
add_runs(p, [("b", {"sup": True, "size": 8.5}), (" 不适用。", {"size": 8.5})])

para("临床医师给出建议的平均用时，闭卷形式为23秒，开卷形式为28秒。相比之下，RAG-LLM工具平均每次建议用时9.7秒。临床医师闭卷和开卷回答的评分者间一致性分别为Fleiss κ=0.294（95% CI 0.291-0.297；P<.001）和Fleiss κ=0.321（95% CI 0.318-0.324；P<.001），表明一致性为一般水平。相比之下，RAG-LLM工具回答的Fleiss κ为1.000（95% CI 0.998-1.000；P<.001），表明一致性极好。")

# =====================================================================
# Discussion
# =====================================================================
h1("讨论")
h2("主要发现")
para("据我们所知，这是泌尿外科领域首个证实RAG-LLM工具用于临床决策支持的有效性的研究。在其他医疗领域，用情境化信息增强LLM已被证明可以减少幻觉并提高准确性[14,15]。在本研究中，RAG-LLM在超过95%的场景中作出了与指南一致的推荐，而低年资临床医师的一致率为60%-75%。")
para("检视与指南不一致的回答后发现，RAG-LLM的错误来自两个方面：（1）CCI计算器的规则化性质，使一名72岁患者尽管前列腺癌危险因素很高，仍被排除在PSA筛查之外；（2）把正常的PSA结果误读为“中度升高”，触发了反应性的重复PSA检测，而这一检测实际上并无必要。相比之下，低年资临床医师的错误散布在众多类别中，与年资和培训状态无关。")
para("我们对RAG-LLM给出的不正确推荐进行了分析，逐一检查每套指南检索到的指南片段、LLM输出以及最终推荐。该场景为一名55岁男性，因勃起功能障碍在接受随访，PSA筛查结果为2.8 ng/mL。从AUA和EAU指南检索到的片段均包含回答该临床场景所需的信息。")
para("就AUA指南而言，RAG-LLM的思维链过程正确识别了“50至69岁人群每2至4年进行一次定期PSA筛查”的合适间隔，但错误地推断2.8 ng/mL的PSA水平为升高，因此建议重复PSA检测。由于检索到的片段中没有任何文字提示2.8 ng/mL的PSA属于升高，我们将该错误归类为幻觉。相反，对于EAU指南，同一片段中包含“PSA最常用的应用阈值为≥3.0 ng/ml”以及“若PSA中度升高（最高至10 ng/mL），应考虑数周后重复检测以确认升高”的表述。RAG-LLM未能把这两条信息综合起来——即“中度升高”的PSA应介于3至10 ng/mL之间——而是把2.8 ng/mL的PSA解读为中度升高。尽管它通过输出“鉴于患者的年龄（55岁）和PSA水平（2.8 ng/mL），他属于可考虑2年随访间隔的类别”显示其认识到了阈值，但随后又推论“参考背景还提示，在PSA中度升高的情况下，应考虑数周后重复检测”，从而建议进行一次不必要的确认性重复PSA检测。")
para("在EAU和AUA指南对PSA检测间隔给出不同推荐的场景中，RAG-LLM工具同时提供了两种推荐。相比之下，低年资临床医师通常只选择一份指南文件作为参考。虽然这并非不正确，但他们的回答在全面性和详尽程度上因此逊于LLM工具生成的回答。")
para("我们的研究表明，RAG-LLM工具有潜力通过实时给出与指南一致的推荐来辅助临床决策。这类临床任务对经验丰富的专科医师而言可能相对简单，但全科医师或低年资临床医师对专科诊疗未必具有同等的熟悉度和经验。此类临床决策支持工具在初级诊疗环境中，或在因时间紧张、患者量大而使高年资医师实际上难以监督每一项临床决策的诊疗环境中，可能证明尤为有用。患者特异的、基于指南的工具有望减轻认知负担、缩短学习曲线、缩短决策用时，从而提高门诊问诊的整体一致性与效率[16]。把RAG-LLM工具用作提高指南依从性的手段，也可以成为减少不必要检查和专科会诊的策略，从而降低患者与公共医疗体系的成本。在初级诊疗环境中，指南依从性的提高已被证明能改善专科转诊的质量与恰当性[17]。")
para("从技术角度看，RAG-LLM工具优于“现成”LLM。在临床医学中使用LLM引发了关于幻觉及由此产生的不准确推荐的担忧，这关系到患者诊疗与安全。在LLM工具中纳入RAG系统可降低幻觉的发生频率[18]，并且比从零开始微调或预训练模型更为经济。")

h2("局限性")
para("我们承认本研究存在一些临床和技术领域的重要局限。首先，从临床角度来看，本研究使用的是虚构病例场景，而非真实临床病例。虽然这可能限制普遍性和外部验证，但可以认为，在一套精心构建的多样化病例场景上评估LLM，比对一般人群抽样（后者不太可能包含少见或复杂病例）更好[19]。这类似于对低年资临床医师的考核：其能力是通过特意设计的病例集，而非一般常见病例样本进行评估的[20,21]。未来的方向包括针对回顾性和前瞻性真实临床病例测试模型稳健性。")
para("第二个临床局限是使用CCI作为估算10年预期寿命的工具。尽管EAU指南推荐将CCI作为估算预期寿命的手段，但它创建于1987年，在现代实践中存在某些局限，例如共病列表不完整、假设共病的影响为可加性，以及现代医疗管理下疾病预后可能更长[22,23]。虽然共病负担和患者剩余健康寿命是任何筛查试验获益的关键决定因素，但目前的评分工具可能无法充分捕捉临床实践和患者评估的细微差别，且确实依赖于集中趋势的队列指标来估算预期寿命。因此，我们设想此类临床决策支持工具将作为“副驾驶”协助临床医师，保持“人在回路”的模式，而不是作为自主决策者运行。此外，该工具设计是模块化的，将CCI判定与病例分析分为先后两个步骤，因此既可以替换为其他共病计算器，临床医师也可以酌情完全省略这一步骤。")
para("第三，从技术角度来看，尽管已证明用RAG补充LLM可降低AI幻觉的发生率[18,24]，但这些模型并不能完全避免幻觉。我们的RAG-LLM工具在1个场景中因幻觉或推理错误给出了不正确的推荐，但其错误方向是保守的，避免了前列腺癌漏诊可能造成的危害。这一错误来源提示，现行文本文件可能需要某种程度未明言的人类推断，而这并非LLM固有的能力。在文本数据中识别这些问题区域并对术语加以明确定义，或可改善基于LLM工具的推理与性能。许多AI或AI辅助工具的“黑箱”性质[25,26]可能使人难以精确定位内部推理过程中的错误，但提示工程、自反式RAG模型等技术手段或有助于提高这些模型的准确性[27]。不同LLM之间的性能差异也需要纳入考量，并与各模型的成本加以权衡。")

h2("未来方向")
para("尽管存在这些局限，RAG-LLM工具在医疗领域仍有多种潜在应用。在同一套基于指南推荐的临床决策支持系统基础上，还可以回顾性地把它用作审计工具，识别临床实践中与指南不一致的环节[28]。此外，与微调或预训练方法相比，RAG方法使未来的指南文件能够更方便地纳入系统，保持工具的时效性、防止过时[29]。基于临床数据的前瞻性真实世界模型验证、多模型评估、可解释性方法的实施，以及把此类RAG-LLM管线从PSA检测扩展到泌尿外科其他领域，都是值得进一步研究的方向。")

h1("结论")
para("在这项基于模拟的比较评估中，我们开发了一个为PSA检测提供临床决策支持的RAG-LLM工具。该工具表现出高准确性，在作出高效且与指南一致的决策方面优于低年资临床医师。使用此类工具有助于提高指南依从性、改善患者诊疗，并优化医疗资源的利用。")

h1("经费来源")
para("本研究由新加坡保健集团杜克-新加坡国立大学（“SingHealth Duke-NUS”）学术医学联合办公室的学术医学慈善基金（Foo Keong Tatt泌尿外科讲席教授基金）资助。")

h1("数据可用性")
para("本研究期间生成或分析的数据集，可在合理请求下向通讯作者索取。")

h1("作者贡献")
CONTRIBS = [
    ("概念化：", "JYMT, DYZL, GGRS"),
    ("数据整理：", "JYMT, RSEL, YGT, KC, KJT"),
    ("形式分析：", "QL, JY, YH, JHT"),
    ("经费获取：", "JSPY, CWSC"),
    ("方法学：", "JYMT, DYZL, GGRS, CWSC"),
    ("软件：", "QL, JY, YH, JHT"),
    ("监督指导：", "JHT, JSPY, CWSC, HSSH"),
    ("验证：", "KC, KJT"),
    ("可视化：", "QL"),
    ("初稿撰写：", "JYMT, RSEL"),
    ("审阅与修改：", "JYMT, DYZL, GGRS, RSEL, KJT, JSPY, CWSC"),
]
for label, names in CONTRIBS:
    labeled(label, names, size=10, after=2)

h1("利益冲突")
para("作者声明无利益冲突。")

h1("多媒体附录1")
para("补充材料，包括RAG-LLM工具的设计与技术要素。LLM：大语言模型；RAG：检索增强生成。")
para("[DOCX文件（Microsoft Word文件），869 KB - 多媒体附录1]",
     size=10, color=RGBColor(0x1F, 0x4E, 0xC0))

# =====================================================================
# References (kept verbatim, as is customary for translations)
# =====================================================================
h1("参考文献")
REFS = [
 "Bray F, Laversanne M, Sung H, et al. Global cancer statistics 2022: GLOBOCAN estimates of incidence and mortality worldwide for 36 cancers in 185 countries. CA A Cancer J Clinicians. May 2024;74(3):229-263. [doi: 10.3322/caac.21834]",
 "Etzioni R, Penson DF, Legler JM, et al. Overdiagnosis due to prostate-specific antigen screening: lessons from U.S. prostate cancer incidence trends. J Natl Cancer Inst. Jul 3, 2002;94(13):981-990. [doi: 10.1093/jnci/94.13.981] [Medline: 12096083]",
 "Pinsky PF, Parnes HL, Andriole G. Mortality and complications after prostate biopsy in the Prostate, Lung, Colorectal and Ovarian cancer screening (PLCO) trial. BJU Int. Feb 2014;113(2):254-259. [doi: 10.1111/bju.12368] [Medline: 24053621]",
 "Cornford P, van den Bergh RC, Briers E, et al. EAU-EANM-ESTRO-ESUR-ISUP-SIOG guidelines on prostate cancer-2024 update. Part I: screening, diagnosis, and local treatment with curative intent. Eur Urol. Aug 2024;86(2):148-163. [doi: 10.1016/j.eururo.2024.03.027] [Medline: 38614820]",
 "Wei JT, Barocas D, Carlsson S, et al. Early detection of prostate cancer: AUA/SUO guideline part I: prostate cancer screening. J Urol. Jul 2023;210(1):46-53. [doi: 10.1097/JU.0000000000003491] [Medline: 37096582]",
 "Kalavacherla S, Riviere P, Javier-DesLoges J, et al. Low-value prostate-specific antigen screening in older males. JAMA Netw Open. Apr 3, 2023;6(4):e237504. [doi: 10.1001/jamanetworkopen.2023.7504] [Medline: 37040113]",
 "Clusmann J, Kolbinger FR, Muti HS, et al. The future landscape of large language models in medicine. Commun Med. Oct 10, 2023;3(1):1-8. [doi: 10.1038/s43856-023-00370-1]",
 "Wang D, Liang J, Ye J, et al. Enhancement of the performance of large language models in diabetes education through retrieval-augmented generation: comparative study. J Med Internet Res. Nov 8, 2024;26(1):e58041. [doi: 10.2196/58041] [Medline: 39046096]",
 "Liu S, McCoy AB, Wright A. Improving large language model applications in biomedicine with retrieval-augmented generation: a systematic review, meta-analysis, and clinical development guidelines. J Am Med Inform Assoc. Apr 1, 2025;32(4):605-615. [doi: 10.1093/jamia/ocaf008] [Medline: 39812777]",
 "Gu Z, Jia W, Piccardi M, Yu P. Empowering large language models for automated clinical assessment with generation-augmented retrieval and hierarchical chain-of-thought. Artif Intell Med. Apr 2025;162(103078):103078. [doi: 10.1016/j.artmed.2025.103078]",
 "Charlson ME, Pompei P, Ales KL, MacKenzie CR. A new method of classifying prognostic comorbidity in longitudinal studies: development and validation. J Chronic Dis. 1987;40(5):373-383. [doi: 10.1016/0021-9681(87)90171-8] [Medline: 3558716]",
 "Death and life expectancy. Statistics Singapore. URL: http://www.singstat.gov.sg/find-data/search-by-theme/population/death-and-life-expectancy/latest-data [Accessed 2024-09-30]",
 "Wei J, Wang X, Schuurmans D, et al. Chain-of-thought prompting elicits reasoning in large language models. In: Koyejo S, Mohamed S, Agarwal A, Belgrave D, editors. NIPS '22: Proceedings of the 36th International Conference on Neural Information Processing Systems. Curran Associates Inc; 2024:24824-24837. ISBN: 9781713871088",
 "Lim DYZ, Tan YB, Koh JTE, et al. ChatGPT on guidelines: providing contextual knowledge to GPT allows it to provide advice on appropriate colonoscopy intervals. J Gastroenterol Hepatol. Jan 2024;39(1):81-106. [doi: 10.1111/jgh.16375] [Medline: 37855067]",
 "Ge J, Sun S, Owens J, et al. Development of a liver disease-specific large language model chat interface using retrieval augmented generation. Gastroenterology. Nov 10, 2023. [doi: 10.1101/2023.11.10.23298364] [Medline: 38451962]",
 "Chen Z, Liang N, Zhang H, et al. Harnessing the power of clinical decision support systems: challenges and opportunities. Open Heart. Nov 2023;10(2):e002432. [doi: 10.1136/openhrt-2023-002432]",
 "Blank L, Baxter S, Woods HB, et al. Referral interventions from primary to specialist care: a systematic review of international evidence. Br J Gen Pract. Dec 2014;64(629):e765-e774. [doi: 10.3399/bjgp14X682837]",
 "Gilbert S, Kather JN, Hogan A. Augmented non-hallucinating large language models as medical information curators. NPJ Digit Med. Apr 23, 2024;7(1):100. [doi: 10.1038/s41746-024-01081-0] [Medline: 38654142]",
 "Bai S, Zhang L, Ye Z, Yang D, Wang T, Zhang Y. The benefits of using atypical presentations and rare diseases in problem-based learning in undergraduate medical education. BMC Med Educ. Feb 6, 2023;23(1):93. [doi: 10.1186/s12909-023-04079-6] [Medline: 36747223]",
 "Surry LT, Torre D, Durning SJ. Exploring examinee behaviours as validity evidence for multiple-choice question examinations. Med Educ. Oct 2017;51(10):1075-1085. [doi: 10.1111/medu.13367] [Medline: 28758233]",
 "Ilgen JS, Bowen JL, McIntyre LA, et al. Comparing diagnostic performance and the utility of clinical vignette-based assessment under testing conditions designed to encourage either automatic or analytic thought. Acad Med. Oct 2013;88(10):1545-1551. [doi: 10.1097/ACM.0b013e3182a31c1e] [Medline: 23969355]",
 "Drosdowsky A, Gough K. The Charlson Comorbidity Index: problems with use in epidemiological research. J Clin Epidemiol. Aug 2022;148:174-177. [doi: 10.1016/j.jclinepi.2022.03.022]",
 "Charlson ME, Carrozzino D, Guidi J, Patierno C. Charlson comorbidity index: a critical review of clinimetric properties. Psychother Psychosom. 2022;91(1):8-35. [doi: 10.1159/000521288] [Medline: 34991091]",
 "Li H, Huang J, Ji M, Yang Y, An R. Use of retrieval-augmented large language model for COVID-19 fact-checking: development and usability study. J Med Internet Res. 2025;27(1):e66098. [doi: 10.2196/66098]",
 "London AJ. Artificial intelligence and black-box medical decisions: accuracy versus explainability. Hastings Cent Rep. Jan 2019;49(1):15-21. [doi: 10.1002/hast.973] [Medline: 30790315]",
 "Starke G, Gille F, Termine A, et al. Finding consensus on trust in AI in health care: recommendations from a panel of international experts. J Med Internet Res. Feb 19, 2025;27:e56306. [doi: 10.2196/56306] [Medline: 39969962]",
 "Jeong M, Sohn J, Sung M, Kang J. Improving medical reasoning through retrieval and self-reflection with retrieval-augmented large language models. Bioinformatics. Jun 28, 2024;40(Suppl 1):i119-i129. [doi: 10.1093/bioinformatics/btae238] [Medline: 38940167]",
 "Goh R, Cook B, Stretton B, et al. Large language models can effectively extract stroke and reperfusion audit data from medical free-text discharge summaries. J Clin Neurosci. Nov 2024;129:110847. [doi: 10.1016/j.jocn.2024.110847] [Medline: 39305548]",
 "Miao J, Thongprayoon C, Suppadungsuk S, Garcia Valencia OA, Cheungpasitporn W. Integrating retrieval-augmented generation with large language models in nephrology: advancing practical applications. Med Bogota Colomb. Mar 8, 2024;60(3):445. [doi: 10.3390/medicina60030445]",
]
for i, ref in enumerate(REFS, 1):
    p = para(f"{i}. {ref}", size=9, after=3)
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.first_line_indent = Cm(-0.6)

h1("缩略语")
for ab, full in [("AI", "artificial intelligence，人工智能"),
                 ("AUA", "American Urological Association，美国泌尿外科学会"),
                 ("CCI", "Charlson Comorbidity Index，Charlson共病指数"),
                 ("EAU", "European Association of Urology，欧洲泌尿外科学会"),
                 ("LLM", "large language model，大语言模型"),
                 ("PSA", "prostate-specific antigen，前列腺特异性抗原"),
                 ("RAG", "retrieval-augmented generation，检索增强生成")]:
    labeled(f"{ab}：", full, size=10, after=2)

# =====================================================================
# editorial / copyright box (single-cell bordered table, as in original)
# =====================================================================
para("", after=4)
box = doc.add_table(rows=1, cols=1)
box.style = "Table Grid"
box.alignment = WD_TABLE_ALIGNMENT.CENTER
cell = box.cell(0, 0)
cell.text = ""

def box_para(parts, size=9, after=4, align=None):
    cp = cell.add_paragraph() if cell.paragraphs[0].runs or len(cell.paragraphs) > 1 else cell.paragraphs[0]
    cp.paragraph_format.space_after = Pt(after)
    if align is not None:
        cp.alignment = align
    add_runs(cp, parts, size=size)
    return cp

box_para([("编辑：", {"bold": True}), ("Andrew Coristine；", {}),
          ("同行评议：", {"bold": True}), ("Monique Beltrão、Ukamaka Modebelu、Yijun Wang；", {}),
          ("投稿日期 ", {}), ("2025年6月2日；终稿收到 2025年10月12日；录用 2025年10月12日；发表 2025年11月19日", {"italic": True})])
box_para([("建议引用格式：", {"bold": True})])
box_para([("Tung JYM, Le Q, Yao J, Huang Y, Lim DYZ, Sng GGR, Lau RSE, Tan YG, Chen K, Tay KJ, Tan JH, Yuen JSP, Cheng CWS, Ho HSS", {})], after=2)
box_para([("Performance of Retrieval-Augmented Generation Large Language Models in Guideline-Concordant Prostate-Specific Antigen Testing: Comparative Study With Junior Clinicians", {"italic": True})], after=2)
box_para([("J Med Internet Res 2025;27:e78393", {})], after=2)
box_para([("URL: https://www.jmir.org/2025/1/e78393", {})], after=2)
box_para([("doi: 10.2196/78393", {})])
box_para([("© Joshua Yi Min Tung, Quan Le, Jinxuan Yao, Yifei Huang, Daniel Yan Zheng Lim, Gerald Gui Ren Sng, Rachel Shu En Lau, Yu Guang Tan, Kenneth Chen, Kae Jack Tay, Jen Hong Tan, John Shyi Peng Yuen, Christopher Wai Sam Cheng, Henry Sun Sien Ho。原文发表于 Journal of Medical Internet Research（https://www.jmir.org），2025年11月19日。本文为开放获取文章，按照知识共享署名许可协议（https://creativecommons.org/licenses/by/4.0/）发布，该协议允许在任何媒介中不受限制地使用、分发和复制，条件是恰当引用原始作品（首次发表于 Journal of Medical Internet Research，ISSN 1438-8871）。必须一并包含完整的书目信息、原发表物的链接（https://www.jmir.org/）以及本版权与许可信息。", {})], after=2, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

doc.save(str(OUT_DOCX))
print("saved:", OUT_DOCX, OUT_DOCX.stat().st_size, "bytes")
