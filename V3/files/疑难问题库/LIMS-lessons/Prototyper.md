# Prototyper · 原型链踩坑录

> 按角色自建自维护；每条 = 现象 → 根因 → 解法。新坑追加在文末，不改旧条。

## 1. dev server 端口 6000 被 Chrome 拒连（ERR_UNSAFE_PORT）

- **现象**：vite 起在 6000，curl 通、浏览器直连报 `ERR_UNSAFE_PORT`。
- **根因**：Chromium 系把 6000–6063 列为 X11 保留端口，客户端直接拒连；服务端探测正常，极易误判成服务没起。
- **解法**：端口从 6000 起避用 6000–6063，本工程固定 6100；详录见 `sunny-lims-prototype/SERVICE.md`。

## 2. `<script lang="jsx">` 的 SFC 热更新后整页 500 / 浏览器停留在旧模块（R7b+R7c，2026-10-22）

- **现象**：页面首次加载正常；HMR 后 lang.jsx 页面在浏览器里报 babel「Unexpected token (6:6)」（code frame 是**模板**的 `@事件` 行）或 import-analysis 500——**用户看到的永远是旧版本页面**，极易误判成「代码改了没生效」。
- **根因**（两层，都要修）：
  1. **HMR `?t=` 后缀 vs include 正则**：HMR 给模块 URL 追加 `?t=时间戳`，`vue2-jsx` 插件 include 写 `/\.[jt]sx$/`（只匹配结尾）不再命中 → JSX 不转换 → 500。解法：include 容忍查询串 `/\.[jt]sx([?&]|$)/`。
  2. **@vitejs/plugin-vue2 脚本子模块竞态**：`xxx.vue?vue&type=script&lang.jsx` 的 load 走 `getResolvedScript(descriptor)`（WeakMap，仅由主模块 transformMain 填充）——主模块尚未转换时返回 undefined → vite 落到 fs 兜底把**整个 SFC** 当模块代码 → babel 把模板当 JSX 解析报 (6:6)。**启动首请求、编辑后 HMR 直取子模块时必现**。解法：vite.config 里加 `enforce: 'pre'` 的 load 插件直接返回 script 块内容（注意 vue 2.7 的 `compiler-sfc.parse({source,...})` **直接返回描述符本体**，不是 `{descriptor}` 包装）。
- **教训**：判断「改了没生效」先分清：curl 该模块 URL（带/不带 `?t=` 都试、冷启动直取子模块）看 transform 是否 200 → 再怀疑业务代码。HMR 徽标绿 ≠ 当前页面模块是最新的。

## 3. umy-ui ux-grid 操作列 push 后不渲染（R7b，2026-10-22）

- **现象**：页面 `state_init()` 里往 `tableAttrs.columns` push「操作列」列，表格里始终不出现。
- **根因**：umy-ui ux-grid 对 `columns` 的 watch 是**引用变化**才 `loadColumn`（`watch: { columns(e){ nextTick(loadColumn(e)) } }`），`push` 原地变更在 created→mount 时序竞态下不触发。
- **解法**：改完列后换一次引用强制重载：`this.<模块>.tableAttrs.columns = this.<模块>.tableAttrs.columns.slice()`。另注意列按钮要从 `tableAttrs.columnTableAttrs` 取（官方 queryListTemplate 同款路径），不是模块 state 根上。

## 4. umy-ui 单元格插槽两条铁律（R7d，2026-10-22，无头浏览器实测定案）

- **现象**：列插槽 `default` 里渲染 el-tag/按钮，表头在、单元格空白（td 的 title 兜底露原始值）。
- **铁律**：
  1. **h 必须用 umy 调用插槽时传入的第 2 参数**：`default: ({ row }, h) => [...]`。页面实例 `$createElement` 造的 vnode 上下文与表格渲染管线不符，**会被静默丢弃**（无任何报错）——实测 span/el-tag 均空白。
  2. **必须返回 vnode 数组** `[h(...)]`，裸 VNode 渲染为空（官方模板/utils.js 的 spanselect 插槽全都是 `[<span>…]` 数组返回，当初照抄 JSX 时丢了这层语义）。
- **教训**：这类「组件库内部调用约定」问题，静态读源码推不出全部行为（本轮连错三轮）；**上无头浏览器（browse skill）跑真实页面 + 运行时逐步换插槽做 A/B 实验**，10 分钟定案。另：umy 表格横向虚拟滚动，**屏外列不渲染**——验证右侧列时先滚动过去再断言。

## 5. 无头浏览器渲染验证当默认步骤 = 每轮白烧 3 分钟（2026-10-27）

- **现象**：起服后顺手跑一遍无头 Chrome（实渲染 + `--dump-dom` + console 抓取 + 截图）当"验证"，一轮 ≈3 分钟，占起服时长的绝大部分。
- **根因**：第 4 条（无头浏览器定案 umy-ui 插槽）被当成了**每轮默认流程**。但它的适用场景是**排错取证**——组件行为反常、需要 A/B 实验时；不是"服务起好了吗"的判据。起服是否成功，用入口页 + 入口模块的 HTTP 200 就够了，渲染验证解决的是另一个问题。
- **解法**：把就绪判据**内建进注册脚本**（`sunny-lims-prototype/scripts/register-dev-task.ps1`）：回收端口 → 注册点火 → 入口页/入口模块双地址 200 → 占端口 PID 归属校验，阻塞到 READY，耗时 ≈13–25 秒；`logs/health-check.json` 的 `ready:true` 即交付门槛。**无头浏览器降级为按需取证**——仅①用户要截图/录屏 ②疑似白屏或表格空（模块 200 但渲染异常）③定稿前留证据 三种情形才跑。
- **教训**：**验证要分"服务活着"与"页面正确"两层**，前者必须便宜且默认，后者昂贵且按需。把昂贵验证塞进默认流程，等于每轮都在为一个不常失败的问题付钱。

## 6. 删计划任务不会停运行实例 → 新实例静默漂端口 → 交付的地址指向旧页面（2026-10-27）

- **现象**：重跑注册脚本"重启"服务，脚本自检全部通过（6100 返回 200），但用户打开地址看到的是**上一版页面**；实际新实例起在 6102（6101 被占），而交付地址报的是 6100。
- **根因**：Windows `Schedule.Service.DeleteTask` **只删注册项，不停已运行的实例**——旧 vite 继续占着 6100。新实例因端口冲突被 vite **静默漂移到下一个可用端口**（vite 默认不 `strictPort`），而双地址探测"6100 有响应"——响应的是旧实例，自检被**骗过**。
- **解法**：三处同时修——
  1. 注册前先 `$t.Stop()` 再 `DeleteTask`（停实例而非只删注册项）；
  2. 回收**本工程路径**下的残留 vite 进程（按精确 PID，先与 `multica daemon status --output json` 的 pid 比对再动手，**不按进程名杀**）；
  3. vite 加 `strictPort: true`——端口被占直接失败退出，不静默漂移；自检另加**实例归属校验**（占端口的 PID 必须是本工程 vite），不匹配就报 DIAG 而非交付。
- **教训**：**"地址能访问"不等于"访问到的是我刚起的那份"**。双地址验证只证明了有东西在应答，没证明应答者是预期的那个。凡是"重启后行为异常"，先查端口归属与进程 PID，不要先怀疑代码。

## 7. 端口写死 = 迟早撞车；随机分配要跨任务互斥 + OS 实测 + 复用（2026-10-27）

- **现象**：原型 dev server 固定用 6100。同机实测已有 **2 个 Multica 任务各起着一个 vite**（6100 / 6102），还各有同名计划任务；再来一个任务就撞。
- **根因**：端口是**机器级资源**，但每个 checkout 的代码副本都以为 6100 是自己的。写死端口 = 把"现在恰好空着"当成了常量。
- **解法**（`sunny-lims-prototype/scripts/allocate-port.mjs`）：区间 6100–6299 内随机取，三重判占用才给——
  1. **剔除 6000–6063**（Chromium 拒访，服务端 curl 却通）；
  2. **跨任务互斥**：`~/.sunny-lims/ports/port-<端口>.lock` 用 `open(O_EXCL)` 原子创建；
  3. **OS 实测**：逐个真实 bind 试探，能发现看不见的占用方。
  再加**重拉复用**：本 checkout 上次的端口仍空闲就继续用——**地址不能漂**，用户已打开的页面不能失效。
- **三个必须避开的坑**：
  1. **锁文件不能放 `os.tmpdir()`**——Multica 运行时把 `TEMP` 指向 `Temp\multica-task-<id>` 子目录，**每个任务各拿一个目录**，锁就形同虚设。要放用户级（`os.homedir()`）目录。
  2. **计划任务名也要唯一**——否则并发任务互相覆盖任务定义。命名带 checkout 后缀（项目路径 sha1 前 8 位）；旧固定名只能靠**动作的 WorkingDirectory 是否等于本工程路径**判定归属，别人的任务不能动。
  3. **端口漂移是隐蔽故障**——vite 默认不 `strictPort`，端口被占就静默换端口，于是"6100 能访问"探到的是旧实例。必须 `strictPort: true` + 实例归属校验（占端口的 PID 必须是本工程 vite）。
- **教训**：**机器级共享资源（端口、锁、缓存）不能用"本工程路径下的文件"来隔离**——每个 checkout 都是独立副本，隔离必须建立在机器级位置 + 操作系统事实上。


