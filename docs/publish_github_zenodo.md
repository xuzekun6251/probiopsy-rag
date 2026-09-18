# GitHub + Zenodo 公开发布步骤清单

> 目标：把本项目作为论文的数据/代码可用性声明所指向的公开仓库发布，并获得 Zenodo DOI。
> 全程只需浏览器 + 本机 git（本机未装 gh CLI，所有 GitHub/Zenodo 操作在网页上完成）。
> `.env`（含 API 密钥）已在 `.gitignore` 中，**不会被推送**——推送前用第 0 步自查一遍。

---

## 0. 推送前自查（一条命令）

```bat
set "PATH=C:\Users\31291\portable-git\cmd;%PATH%"
git status --short
```

确认看不到 `.env`、`data/_local_only/`、`data/raw/`、`data/processed/`。若 `git status` 输出为空，说明当前已全部提交，正常。

---

## 1. 填写作者信息并传播（本地）

1. 打开 `configs/author_info.yaml`，填写 PI（中英文名、职称、科室、单位、邮箱）、合作者（姓名/科室/单位/贡献）、基金、利益冲突、`github_repo`、`zenodo_doi`（先留空）。
2. 运行：

```bat
.venv\Scripts\python.exe scripts\apply_author_info.py
```

它会替换 manuscript.en.md / 00_front_zh.md / cover_letter.md / data_availability.md / LICENSE / .zenodo.json 中的全部 TODO，重拼中文稿并重建投稿 zip。脚本末尾若列出"剩余 TODO"需手工处理。

---

## 2. 版权决策点：ProBIOPSY 原文能否随仓库公开？✅ 已核实（2026-09）：原文为 **CC BY**

> **结论：无需脱敏，原样发布。** 署名要素已在三处落实：`data_availability.md`（Licensing 段）、`LICENSE`（third-party notice）、`.zenodo.json`（notes），均注明 CC BY 4.0、verbatim 未修改、来源 DOI。`data/processed/`（含共识文本的 LightRAG 索引）本就在 `.gitignore` 中不会上传。
> 以下表格保留作背景与备查：

`data/seed/probiopsy_statements.csv` 含 `statement_text_en` 列（共识原文全文），`data/evidence/` 及 LightRAG 索引亦含共识文本。这些内容的版权属于 Elsevier，**是否可再分发取决于原文的 OA 许可证**：

1. 用机构访问打开 <https://doi.org/10.1016/j.eururo.2026.06.012>，在文章页找 **Open Access / License 徽标**（通常在标题下方或 PDF 首页脚注）。
2. 按结果二选一：

| 原文许可 | 处理方式 |
|---|---|
| **CC BY** 或 **CC BY-NC-ND**（Elsevier OA 常见徽标） | 可随仓库发布（保留来源署名与 DOI，ND 条款要求不得修改原文文本——我们未改动，仅切分引用，合规）。把核实到的许可写进 `data_availability.md` Licensing 段。 |
| **© Elsevier（subscription / all rights reserved）或查不到** | 运行脱敏后再发布：`scripts\scrub_statement_text.py scrub` —— 删除 `statement_text_en` 列、把 `data/evidence/` 移入 git 忽略的 `data/_local_only/`。仓库仍保留 statement_id、领域、标签、决策项与 locator，代码与预测结果完整可复现评审链。 |

> 注意：`data_availability.md` 第 17 行现称"only statement numbers and short locators are redistributed"——若选择原样发布（未脱敏），请把该句改为与实际相符的表述（如 "statement text is redistributed under the article's CC BY license"）。

---

## 3. 创建 GitHub 仓库并推送

1. 浏览器登录 GitHub → 右上角 **+** → **New repository**：
   - Repository name 建议 `probiopsy-rag`；
   - **Public**；**不要**勾选 README / .gitignore / license 初始化（本地已有）；
2. 本地推送（在 `D:\Zcode测试文件夹\测试3`）：

```bat
set "PATH=C:\Users\31291\portable-git\cmd;%PATH%"
git remote add origin https://github.com/<你的用户名>/probiopsy-rag.git
git push -u origin master
```

（若提示登录，用浏览器完成 GitHub 授权即可；用户名替换 `<你的用户名>`。）

3. 把仓库 URL 填进 `configs/author_info.yaml` 的 `github_repo`，重跑第 1 步的 apply 脚本。

---

## 4. 打发布标签（Zenodo 自动归档依赖 Release）

```bat
git tag -a v1.0.0 -m "First public release: manuscript submission version"
git push origin v1.0.0
```

---

## 5. 获取 Zenodo DOI（推荐路线 A：GitHub 联动）

**路线 A（推荐，一次配置永久生效）：**

1. 浏览器登录 <https://zenodo.org>（用 GitHub 账号 OAuth 登录最方便）。
2. 右上角头像 → **GitHub** → 找到 `probiopsy-rag` → 把开关拨到 **On**（允许 Zenodo 访问该仓库）。
3. 回到 GitHub 仓库 → **Releases** → **Draft a new release** → 选择刚推送的 tag `v1.0.0` → Publish release。
4. Zenodo 自动抓取该 Release 并生成 DOI（首次约几分钟）。仓库根目录的 `.zenodo.json` 提供元数据（标题、作者、许可、关键词、关联共识 DOI）；作者名单来自 apply 脚本写入的 `creators` 字段。
5. 记下 DOI（形如 `10.5281/zenodo.XXXXXXX`）。

**路线 B（备选，手动上传）：** Zenodo → **New upload** → 上传 `outputs/submission/` 里的投稿 zip（或仓库 zip）→ 手工填 `.zenodo.json` 同款元数据 → Publish。

---

## 6. DOI 回填并二次提交

1. 把 Zenodo DOI 填进 `configs/author_info.yaml` 的 `zenodo_doi`，重跑 `apply_author_info.py`（会自动写入 `data_availability.md`）。
2. 手工把 README.md 尾部 bibtex 里的 `10.5281/zenodo.XXXXXXX` 和 `https://github.com/<user>/probiopsy-rag` 替换为真实值。
3. 提交并推送：

```bat
git add -A .
git commit -m "Fill Zenodo DOI and repo URL"
git push
```

4. （可选）在 Zenodo 该记录页点 **New version** 归档更新版；论文修稿阶段用同一 DOI 的版本号机制即可。

---

## 7. 发布后终检

- [ ] 匿名浏览器打开仓库 URL，确认：无 `.env`、无专家姓名/单位、无患者信息；
- [ ] README、LICENSE、`.zenodo.json` 三个文件的作者/单位一致；
- [ ] Zenodo 记录页元数据（作者、许可、关联 DOI）正确显示；
- [ ] 论文 `data_availability.md` 的仓库 URL 与 Zenodo DOI 可点击且有效。
