# PackHubGlobe GEO 实施与验收 — 2026-10-30

状态以 2026-11-04 深度优化记录为准。GSC/Bing 提交与 AI 可见性基线仍待执行。

## 已完成

- 保留 www 规范域名、现有 1,824 个目录产品、询盘流程、工厂视频与文档。
- 全站 WebSite、WebPage、Organization 通过固定品牌 ID 关联；补齐品牌销售联系入口、页面描述、社交卡片和图片说明。采购指南 Article 引用同一品牌实体。
- 首页用可抓取的具体业务摘要解释产品范围、采购动作；19 篇指南把 Quick answer 放在章节正文前。
- 新增 9 篇英文指南，每篇约 800 词：独立摘要、比较表、采购示例、常见错误、检查清单、4 个 FAQ、资料与产品链接。示例明确为 illustrative，既有概念图标明设计参考。
- 12 个首页、产品、行业、材料、服务和询盘入口添加相关采购指南链接；Resources 自动列出全部 19 篇指南。
- sitemap 现含 2,255 个规范 URL。19 篇指南与指南索引因新增产品参考和导航，于 2026-11-04 更新 sitemap 的 lastmod。
- llms.txt 扩充核心产品、行业、材料、服务及全部指南的说明和链接，作为补充目录。
- robots 保持公开页面可抓取及现有训练策略；补充排除 QA/Git 路径，Apache 配置阻止 QA 文件公开。
- 新增 20 个固定英语采购问题的监测 CSV。所有结果均为 not_measured，没有虚构基线。

## 方案 12 个优先主题对照

| 方案主题 | 实际路径 |
|---|---|
| Quote checklist | /guides/packaging-quote-checklist/ |
| Rigid vs folding | /guides/folding-cartons-vs-rigid-boxes/ |
| Straight vs reverse tuck | /guides/straight-vs-reverse-tuck-end/ |
| Materials | /guides/packaging-materials-explained/ |
| MOQ | /guides/custom-packaging-moq/ |
| Sample process | /guides/packaging-sample-types/ + /services/sampling/ |
| Foil / UV / embossing | /guides/foil-vs-spot-uv-vs-embossing/ |
| Cosmetics | /guides/cosmetic-packaging-buyers-guide/ |
| Apparel | /guides/apparel-packaging-selection/ |
| Dielines | /guides/prepare-packaging-dielines/ |
| Supplier selection | /guides/choose-packaging-supplier-china/ |
| Paper bags | /guides/custom-paper-bags-guide/ |

现有 /about/、/factory/、/services/quality-control/ 和 /request-quote/ 分别承担主体、制造、质量及联系功能，不另建重复路径。

## 验收证据

- `python3 tools/build.py`：2,255 个公开页面 + 404。
- `python3 tools/validate.py`：2,255 个 H1、canonical、唯一标题/描述、sitemap 一致性、185,747 条站内链接、1,858 个引用资源、2,256 段 JSON-LD、全站可达性通过，0 错误。
- `python3 tools/validate-expansion.py`：1,824 个目录产品和全部 19 篇指南内容检查通过；每篇指南至少 700 词。
- `tools/test-ux.cjs`：54 组响应式页面、10 组 WCAG 自动检查、3 组任务通过。询盘响应由测试模拟，未发送邮件。
- `tools/test-geo.cjs`：9 篇新指南关闭 JS 后的 HTTP/结构/答案/FAQ 检查、18 组手机及桌面布局、2 组 WCAG 自动检查通过；没有图片加载失败或横向溢出。
- `node tools/test-enquiry.mjs`、`node tools/test-media.mjs`：询盘前端成功/失败/附件限制、上下文捕获、视频控制与减少动态效果检查通过。
- JS 语法和 `git diff --check` 通过。PHP 运行时未安装，PHP 服务端测试未运行；此次未改 PHP。
- 截图与 JSON 结果：`qa/geo/`、`qa/ux/`、`qa/validation.json`、`qa/depth/acceptance.json`。QA 不进入部署 ZIP，Apache 规则也阻止访问该目录。

## 当前线上基线与剩余工作

2026-10-30 HTTP 检查：首页、robots、sitemap、llms、About、Factory、分类、目录、原有指南和询盘页均 200；裸域名 301 到 www；随机不存在路径 404。外部搜索读取工具不能读取首页，因此不能由该工具失败推断停机。HTTP 抽查不能证明所有网络、手机运营商或真实爬虫 IP 可达，也不能替代 WAF 日志。

以上为首次优化前的线上基线。Hostinger 发布后须比对新指南、首页、robots、sitemap 与 llms 的内容及状态，并检查 Apache 保护与规范跳转。

仍待完成的账户/业务事项：

1. 核对 Hostinger 部署是否使用本轮 GitHub main 提交，并比对公开页面与产物。
2. 在已验证的目标 GSC/Bing 账户中查看属性、sitemap 和索引状态；未提交、未声称索引成功。IndexNow 尚未建立验证密钥或提交。
3. 检查 WAF 日志中的真实抓取请求；仅更换 User-Agent 不能证明真实爬虫的网络通行。
4. 方案要求的 3 个可核验客户案例仍缺少订单资料和公开授权，没有以概念图替代。公司资料采用既有 About/Factory 信息，未新增未经验证的法律主体、规模、客户、认证或测试结论。
5. GA4 或其他真实采集器尚未连接。现有 dataLayer 事件可供后续接入，但不能当作已采集的访问、AI 来源或有效询盘；CRM 归因与询盘质量也尚未建立。
6. 在有可用账户的独立会话中执行 CSV 的固定问题，记录引擎、时间、地点、引用 URL 和明确推荐；当前无 AI 引用、流量或商业效果证据。
7. 第三方资料、企业目录与授权客户评价需要相应账户和真实资料，未创建虚假外链或评价。

## 参考资料的角色

- OpenAI crawler documentation：公开检索与训练策略可分开；未改变原有训练许可。https://developers.openai.com/api/docs/bots
- Google AI features：以可索引、可读、相关的内容为基础，llms 文件不作为成功保证。https://developers.google.com/search/docs/appearance/ai-features
- Adobe：印刷色彩管理、出血和印刷标记概念。https://helpx.adobe.com/illustrator/using/printing-color-management.html 与 https://helpx.adobe.com/illustrator/using/printers-marks-bleeds.html
- FSC：材料标签说明，不证明本网站所有产品带相应声明。https://fsc.org/en/label
- ISTA：分销测试程序选择，不作为本企业产品通过测试的证明。https://www.ista.org/test_procedures.php
- MOQ 起点沿用现有 catalog；最终供应主体和商业条款以既有 About、Terms 及订单报价为准。

## 2026-11-04 深度优化

- 1,824 个产品详情的首屏摘要纳入参考编号、材料和 500 件起订说明。产品目录按结构提供采购指南链接，并保留按规格与数量询价的方式。
- 19 篇采购指南各链接 3 个按主题选取的目录参考。指南索引按采购决策提供入口，列表标记与实际可见指南一致。
- 连接 1,824 个 Product、44 个 Service、19 个 Article 和 323 个 ItemList 至对应页面。产品面包屑包含主要分类，分享图与图像说明对应页面内容。
- 通过全站 URL 与 JSON-LD 图谱检查。检查范围包括实体回链、列表成员可见性、面包屑目标、指南日期、参考卡数量、产品分享图及首屏编号和数量。
- 用户授权提交并推送至 GitHub。生产状态以公开站点的内容校验为准。
