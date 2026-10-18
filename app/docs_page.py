"""Custom Chinese Swagger UI page for the ticket triage API."""

from fastapi.responses import HTMLResponse

SWAGGER_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>客服工单优先级分类 API - 接口文档</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
  <style>
    body { margin: 0; background: #f4f6f8; }
    .guide { max-width: 1160px; margin: 24px auto 12px; padding: 22px 26px; border: 1px solid #d8e1e8; border-radius: 12px; background: #ffffff; box-shadow: 0 4px 14px rgba(24, 45, 70, 0.07); font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif; color: #243b53; }
    .guide h1 { margin: 0 0 8px; font-size: 24px; }
    .guide p { margin: 0 0 14px; color: #52667a; }
    .guide ol { margin: 0; padding-left: 22px; line-height: 1.9; }
    .guide code { padding: 2px 6px; border-radius: 4px; background: #edf2f7; color: #b42318; font-family: Consolas, monospace; }
    .tips { margin-top: 14px; padding: 12px 16px; border-left: 4px solid #1677ff; border-radius: 6px; background: #f0f7ff; color: #31465d; line-height: 1.8; }
    #swagger-ui { max-width: 1160px; margin: 0 auto 40px; padding: 0 20px; }
    #swagger-ui .topbar { display: none; }
    #swagger-ui .opblock-summary-path { font-weight: 700; }
    #swagger-ui .info li, #swagger-ui .info p, #swagger-ui .info title { color: #243b53; }
  </style>
</head>
<body>
  <section class="guide" aria-labelledby="docs-title">
    <h1 id="docs-title">接口使用说明</h1>
    <p>本页面用于测试客服工单优先级分类 API。你可以直接在页面上输入工单内容，查看模型预测结果。</p>
    <ol>
      <li>找到接口 <code>POST /triage</code>，点击展开。</li>
      <li>点击右上角 <code>试一试</code> 按钮。</li>
      <li>修改请求体中的 <code>text</code>、<code>customer_tier</code> 和 <code>monthly_revenue</code>。</li>
      <li>点击 <code>执行</code>，在下方“服务器返回”区域查看预测结果。</li>
      <li>如果想确认模型是否正常加载，可以测试 <code>GET /health</code>。</li>
    </ol>
    <div class="tips">
      提示：<code>customer_tier</code> 只能填 <code>free</code>、<code>standard</code> 或 <code>premium</code>。优先级返回值含义：<code>urgent</code> 紧急、<code>high</code> 高、<code>normal</code> 普通、<code>low</code> 低。
    </div>
  </section>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js" crossorigin></script>
  <script>
    window.onload = () => {
      window.ui = SwaggerUIBundle({
        url: "/openapi.json",
        dom_id: "#swagger-ui",
        deepLinking: true,
        docExpansion: "list",
        defaultModelsExpandDepth: 1,
        defaultModelExpandDepth: 1,
        tryItOutEnabled: true,
        persistAuthorization: true,
        layout: "BaseLayout"
      });

      const translations = new Map([
        ["Try it out", "试一试"],
        ["Execute", "执行"],
        ["Clear", "清空"],
        ["Close", "关闭"],
        ["Loading...", "正在加载接口文档..."],
        ["Request body", "请求体"],
        ["Parameters", "请求参数"],
        ["No parameters", "无需请求参数"],
        ["Responses", "服务器返回"],
        ["Response body", "响应内容"],
        ["Response headers", "响应头"],
        ["Example Value", "示例值"],
        ["Models", "数据模型"],
        ["Schemas", "数据结构"],
        ["Schema", "数据结构"],
        ["Required", "必填"],
        ["Description", "说明"],
        ["Name", "名称"],
        ["Links", "链接"],
        ["Online documentation", "在线文档"]
      ]);

      const translateNodes = (root) => {
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
          const node = walker.currentNode;
          const original = node.nodeValue.trim();
          if (translations.has(original)) {
            node.nodeValue = node.nodeValue.replace(original, translations.get(original));
          }
        }
      };

      translateNodes(document.body);
      new MutationObserver(() => translateNodes(document.body)).observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
      });
    };
  </script>
</body>
</html>"""


def chinese_swagger_page() -> HTMLResponse:
    """Return a Swagger UI page with Chinese usage instructions."""
    return HTMLResponse(SWAGGER_HTML)
