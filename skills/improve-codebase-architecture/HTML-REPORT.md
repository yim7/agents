# HTML 报告格式

架构审查渲染为操作系统临时目录中的一个自包含 HTML 文件。Tailwind 和 Mermaid 都从 CDN 引入。Mermaid 能可靠地处理图状的图形；手写的 div 和内联 SVG 处理更有编辑感的图形（体量图、剖面图）。两者混用：不要什么都靠 Mermaid，否则看起来会很千篇一律。

## 骨架

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <title>{{仓库名}} 架构审查</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      /* 一小层自定义样式，处理 Tailwind 不方便覆盖的东西：
         虚线接缝、手绘感的箭头等。 */
      .seam { stroke-dasharray: 4 4; }
      .leak { stroke: #dc2626; }
      .deep { background: linear-gradient(135deg, #0f172a, #1e293b); }
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

仓库名、日期和一个紧凑的图例：实线框 = 模块，虚线 = 接缝，红色箭头 = 泄漏，粗深色框 = 深模块。没有介绍段落。直接进入候选项。

## 候选项卡片

图形承担主要分量。文字稀疏、平实，不加修饰地使用术语表（来自 [CODEBASE-DESIGN.md](CODEBASE-DESIGN.md)）中的术语。

每个候选项是一个 `<article>`：

- **标题**：简短，点明这次加深（例如“合并订单接收流水线”）。
- **徽章行**：推荐强度（`Strong` = 祖母绿，`Worth exploring` = 琥珀色，`Speculative` = 石板灰），加上一个依赖分类标签（`in-process`、`local-substitutable`、`ports & adapters`、`mock`）。
- **文件**：等宽列表，`font-mono text-sm`。
- **前后对比图**：核心部分。两栏左右并排。见下面的图形模式。
- **问题**：一句话。哪里疼。
- **方案**：一句话。改什么。
- **收益**：要点列表，每条不超过 6 个词。例如“测试只打一个接口”“定价逻辑不再泄漏”“删掉 4 个浅包装”。
- **ADR 提示框**（如适用）：琥珀色底框里的一行字。

不要写解释性的段落。如果一张图需要一段话才能看懂，就重画这张图。

## 图形模式

选择适合该候选项的模式。混着用。不要让每张图看起来都一样。多样性本身就是目的之一。

### Mermaid 图（表达依赖／调用流的主力）

当要表达的是“X 调用 Y 调用 Z，看看这一团乱”时，用 Mermaid 的 `flowchart` 或 `graph`。把它包在一张 Tailwind 样式的卡片里，让它不显得突兀。用 classDef 把泄漏的边染成红色，把深模块染成深色。时序图很适合表达“之前：6 次往返；之后：1 次”。

```html
<div class="rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      A[OrderHandler] --> B[OrderValidator]
      B --> C[OrderRepo]
      C -.leak.-> D[PricingClient]
      classDef leak stroke:#dc2626,stroke-width:2px;
      class C,D leak
  </pre>
</div>
```

### 手绘方框和箭头（当 Mermaid 的布局跟你作对时）

模块是带边框和标签的 `<div>`。箭头是绝对定位在相对容器上的内联 SVG `<line>` 或 `<path>`。当你希望“之后”的图看起来像一个粗边框的深模块、内部细节变灰时，用这种方式，因为 Mermaid 渲染不出那种分量感。

### 剖面图（适合层层叠叠的浅）

堆叠水平条带（`h-12 border-l-4`），展示一次调用要穿过的层。之前：6 个薄层，每层什么都不做。之后：1 个厚条带，标注合并后的职责。

### 体量图（适合“接口和实现一样宽”）

每个模块两个矩形：一个代表接口表面积，一个代表实现。之前：接口矩形几乎和实现矩形一样高（浅）。之后：接口矩形很矮，实现矩形很高（深）。

### 调用图折叠

之前：一棵函数调用树，渲染成嵌套的方框。之后：同一棵树折叠成一个方框，原来的调用变成内部调用，在框内淡化显示。

## 样式指导

- 偏编辑风格，而不是企业仪表盘风格。留白要大方。标题可以用衬线体（`font-serif` 和 stone/slate 搭配效果很好）。
- 节制用色：一个强调色（祖母绿或靛蓝），加上红色表示泄漏、琥珀色表示警告。
- 图形高度约 320px，让前后对比能左右并排、无需滚动。
- 图形中的模块标签用 `text-xs uppercase tracking-wider`，让它们读起来像示意图，而不是界面。
- 只有 Tailwind CDN 和 Mermaid ESM 导入这两个脚本。报告其余部分都是静态的：没有应用代码，除了 Mermaid 自身的渲染之外没有交互。

## 首要推荐一节

一张更大的卡片。候选项名称、一句理由、指向它卡片的锚点链接。就这些。

## 语气

平实、简洁，但架构名词和动词直接来自 [CODEBASE-DESIGN.md](CODEBASE-DESIGN.md)。简洁不是漂移的借口。

**严格使用：** 模块、接口、实现、深度、深、浅、接缝、适配器、杠杆、局部性。

**不要替换成：** 组件、服务、单元（代替模块）· API、签名（代替接口）· 边界（代替接缝）· 层、包装（当你指的是模块时）。

**符合风格的说法：**

- “订单接收模块是浅的：接口几乎等于实现。”
- “定价逻辑跨过接缝泄漏。”
- “加深：一个接口，一个测试位置。”
- “两个适配器证明了这个接缝：生产用 HTTP，测试用内存。”

**收益要点**用术语表的词说明收获：*“局部性：bug 集中在一个模块”*、*“杠杆：一个接口，N 个调用点”*、*“接口缩小；实现吸收了包装层”*。不要写*“更易维护”*或*“代码更整洁”*，因为这些词不在术语表里，不值得占位置。

不要含糊其辞，不要清嗓子式的开场，不要“值得注意的是……”。能写成要点的句子就写成要点。能删的要点就删。如果一个词不在 [CODEBASE-DESIGN.md](CODEBASE-DESIGN.md) 的术语表里，先找一个在表里的词，再考虑造新词。
