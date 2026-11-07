# HTML 报告格式

报告是一个自包含的 HTML 文件，只从 CDN 引入 Tailwind（排版）和 Mermaid（画图）两个脚本，其余都是静态内容。

## 骨架

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <title>{{仓库名}} 架构体检</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      .seam { stroke-dasharray: 4 4; }   /* 接缝画虚线 */
      .leak { stroke: #dc2626; }         /* 跨模块泄漏画红线 */
      .diagram { max-height: 360px; overflow: auto; }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="candidates" class="space-y-10">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## 页头

仓库名、日期、提交号，加一行图例：实线框是模块，虚线是接缝，红色箭头是泄漏，粗深色框是深模块。不写介绍段落。

## 候选卡片

每个候选一个 `<article>`，内容按这个顺序：

- **标题**：一句话点明改什么，例如“汇率对规则收进一个模块”。
- **标签**：推荐程度（强烈用绿色、值得探索用琥珀色、存疑用灰色）和依赖类别。
- **涉及文件**：等宽字体列表。
- **前后对比图**：左右两栏，左边现状，右边改后。这是卡片的主体。
- **问题**：一两句，写具体现象和证据，例如“23 处 `isRatio` 分支散在 10 个文件”。
- **方案**：一两句，写改什么。
- **好处**：短句列表，写可核实的变化，例如“规则只在一处”“删掉 7 个转手函数”“新增的测试不用起服务”。“更易维护”“更整洁”这类说不出具体变化的不写。
- **与已定决定冲突**（如有）：琥珀色底的一行，写明冲突的是哪条决定、为什么值得重提。

图看不懂就重画图，不靠加一段解释。

## 选哪种图

按要表达的内容选：

- **调用和依赖关系**（谁调用谁、哪里绕了几圈）：Mermaid `flowchart`，泄漏的边用 `classDef` 染红。调用次数的前后变化用时序图。
- **一次调用要穿过几层**：横向条带叠起来，左边是很多薄层，右边是合并后的一层。
- **接口和实现一样大**：每个模块画两个矩形，一个代表接口、一个代表实现。改前两个差不多高，改后接口矮、实现高。
- **一棵调用树被收进一个模块**：左边嵌套方框，右边一个方框，原来的调用在框内淡化显示。

后三种用普通的 `div` 和内联 SVG 手画。

```html
<div class="diagram rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      A[OrderHandler] --> B[OrderValidator]
      B --> C[OrderRepo]
      C -.泄漏.-> D[PricingClient]
      classDef leak stroke:#dc2626,stroke-width:2px;
      class C,D leak
  </pre>
</div>
```

## 样式

- 留白充足，一个强调色（绿或靛蓝），红色只用于泄漏，琥珀色只用于警告。
- 前后对比两栏并排；图高控制在 360px 左右，Mermaid 遇到中文或节点多时高度不可控，用 `.diagram` 的 `max-height` 加滚动兜底。

## 最后一节：首要推荐

一张大一点的卡片：候选名称、一句理由、跳到对应卡片的链接。

## 交付前检查

在浏览器里打开一次：Tailwind 样式生效，每个 Mermaid 块都变成了图（语法错误只在渲染时暴露），控制台没有报错。
