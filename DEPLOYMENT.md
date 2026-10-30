# Hostinger 部署说明

目标域名：**https://www.packhubglobe.com/**
GitHub：**https://github.com/andrewzhuo123-ui/packhubglobe**
分支：**main**
网站根目录：**public_html**

## 方法一：从 GitHub 部署

本仓库根目录就是网站文件根目录，已有 `index.html`、`assets/`、`products/`、`industries/`、`.htaccess`、`robots.txt`、`sitemap.xml` 等。

1. 在 Hostinger 中为 packhubglobe.com 使用支持自定义 HTML / PHP 文件的站点。
2. 进入目标站点的 **Advanced → Git**，连接有权访问此仓库的 GitHub 账户，并选择 `andrewzhuo123-ui/packhubglobe`。
3. 分支选择 `main`，部署目录使用 `public_html`。不需要 npm、构建命令或启动命令。
4. 首次部署前确认目标目录没有需要保留的网站文件；有旧文件时先备份，不要直接覆盖未知站点。
5. 如需 Git 推送后自动更新，在该目标站点开启 Auto-deployment。

Hostinger 的选项可能随账号和套餐不同，按目标站点显示的 Git 设置操作。不要选 Node.js Web App 或 AI Website Builder 来运行这份纯静态站。

官方说明：https://www.hostinger.com/support/1583302-how-to-deploy-a-git-repository-in-hostinger/

## 方法二：上传部署包

在本地仓库根目录运行 `python3 tools/package.py`，得到 `packhubglobe-hostinger-public_html.zip`。也可使用随本次交付提供的同名压缩包。

把压缩包内容解压到目标站点的 `public_html`。解压后应直接出现 `public_html/index.html`，不要多包一层 `website/`。**需要包含隐藏文件 `.htaccess`**，它负责规范域名、真实 404 和禁止访问源文件目录。

## 域名与检查

- 为根域和 `www` 配置正确的 DNS 与 TLS。网站规范域名为 `https://www.packhubglobe.com/`；裸域和 HTTP 应跳到它。
- 首页、产品详情、行业页、材料页、采购指南和询盘页应能直接刷新访问。
- 随机不存在地址应返回 HTTP 404，并显示品牌 404 页面。
- `https://www.packhubglobe.com/sitemap.xml` 应含 2,247 个规范 URL；`robots.txt` 指向同一个 sitemap。
- `/tools/`、`/content/`、`/.git/`、`README.md` 和 `DEPLOYMENT.md` 不应公开。Git 部署时它们由 `.htaccess` 拦截；ZIP 部署包完全不含这些文件。
- 手机打开菜单、选择分类、展开问答、填写表单并下载简报。
- 邮件询盘入口为 **andrew@packhubglobe.com**；全站 WhatsApp 悬浮入口为 **+86 15105916426**。表单通过 `request-quote/send.php` 使用主机 PHP `mail()` 投递，需启用 PHP 和邮件发送能力。上线后须提交一封明确标识的测试询盘，并核实收件箱实际收到；接口成功仅表示邮件传输服务接受。主机发送失败时返回 503，页面保留输入并提供直接邮箱和 WhatsApp。
- 收录、排名、邮箱实际接收与 Hostinger 上线都需要分别验证，不由 GitHub 推送自动证明。

GitHub 推送完成后，仍需在 Hostinger 部署并检查公开站点；Git 推送不等于上线。首页首屏使用产品组合图；工厂视频位于生产能力模块，由访客主动播放。视频和证书文件均保留在 assets/ 中。
