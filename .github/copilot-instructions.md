# Copilot / AI Agent Instructions for icode_test_platform

简短说明（目标）
- 这是一个基于 Flask 的小型后台运维/导入工具集，包含若干蓝图（Blueprint）模块，用于订单导入、唤醒、短信、解绑、DM 流程等。AI 任务通常是：实现/改进某个蓝图的接口、修复 SQL、写脚本来操作数据库或导入文件、维护自动化运维脚本。

关键位置 & 架构速览
- `app.py` — 程序入口，注册了所有蓝图（见 `ops/*`），并配置了 `UPLOAD_FOLDER`（由 `conf/readconfig.rootPath()` 计算）。
- `ops/` — 核心业务蓝图目录。每个子目录通常会导出一个 Flask Blueprint（例如 `ops/order/orderV2.py` 中的 `app_order_V2`），并在 `app.py` 中通过 `app.register_blueprint(...)` 挂载。
- `lib/py/` — 一组可复用脚本/工具（比如批量导入、短信、各类独立脚本）。这些文件通常由运维或手动脚本调用。
- `bin/runMySQL.py` — 项目统一的 MySQL 访问封装，使用 `conf/config.ini` 中的节名（如 `MySQL-Liuyi-test`）进行实例化： mysqlMain('MySQL-Liuyi-test')。
- `conf/config.ini` — 运行时的所有外部服务 URL 与数据库配置；多数数据库/环境名被硬编码为字符串键供 `bin/runMySQL.py`/`conf/readconfig.py` 使用。
- `templates/` 和 `static/` — 前端模板与静态资源（导入页面、客户页面等）。
- `docs/import_files` — 前端上传文件的存放目录（由 `UPLOAD_FOLDER` 指向）。
- `Dockerfile`, `quick_start.sh`, `gunicorn.conf.py` — 容器化与部署相关（Docker 镜像、运行端口 8003，gunicorn 配置使用 gevent）。

如何本地运行（开发／调试）
- 本地快速启动（开发）：
  - 确保 `conf/config.ini` 中的测试环境条目可访问或替换为本地测试库（注意：该文件包含敏感信息，不要将真实凭据提交到公共仓库）。
  - 运行：
    - 直接启动 Flask（调试模式）: `python app.py`（app.py 中默认绑定为 10.200.13.188:8088，调试本地请改为 `127.0.0.1` 或编辑该行）。
    - 生产式/接近真实：`gunicorn app:app -c gunicorn.conf.py`（默认绑定 `0.0.0.0:8003`，workers=5，worker_class=gevent）。
- Docker：参见 `Dockerfile`。典型流程（在 Linux/Mac）：
  - 构建：`docker build -t testflask .`
  - 运行：`docker run -d -p 8003:8003 testflask`
  - quick_start.sh 提供了仓库拉取、构建并运行容器的样板脚本（在 CI/部署服务器上使用）。

数据库与配置注意事项
- DB 封装：使用 `bin/runMySQL.py` 创建连接，传入 `conf/config.ini` 中的节名（例如 `MySQL-Gubi-test`）。调用方式示例：
  - mysql_conn = mysqlMain('MySQL-Liuyi-test')
  - `execute`, `fetchall`, `fetchone` 都会在连接对象上运行并在内部 commit（注意事务与游标的自动提交行为）。
- 配置：`conf/readconfig.py` 中 `getConfig(sysname, key)` 会读取 `conf/config.ini` 并 eval 字符串（config 文件中的值通常用引号）。不要在公共提交中包含真实密码。

代码风格与约定（仓库特定）
- 每个 `ops/*` 子目录通常暴露一个名为 `app_<feature>` 的 Blueprint 变量并在 `app.py` 中以 `url_prefix` 挂载。例如：
  - `ops/order/orderV2.py` → `app_order_V2`; 挂载路径 `/order_V2`。
- SQL 与数据访问混杂在蓝图实现中（直接使用 `mysqlMain` 执行字符串 SQL）。因此：
  - 修改 SQL 时务必检查 `mysqlMain` 连接使用的是哪个环境（test / preprod）。
  - 优先添加参数化查询以防注入（目前多处使用字符串格式化构造 SQL）。
- 文件编码与本地化：多数文件以 UTF-8，并含有中文注释。

常见 AI 任务示例（如何着手）
- 新增接口或蓝图路由：
  - 在 `ops/<area>/` 新建 `.py`，定义 Flask Blueprint（参考 `ops/order/orderV1.py`），在 `app.py` 注册并设置 `url_prefix`。
- 修复 DB 脚本错误：
  - 找到调用 `mysqlMain(...)` 的位置（示例：`lib/py/dm_script.py` 或 `ops/*`），在本地用测试配置运行并打印 `sql` 与 `sql_result` 来调试。
- 插件/依赖更新：
  - 修改 `requirements.txt`，在虚拟环境中运行 `pip install -r requirements.txt` 验证无破坏性变更。

安全提醒（必须注意）
- `conf/config.ini` 含多项真实/示例凭据，请勿将含敏感数据的更改推送到公共仓库；CI 或开发人员可用占位/环境变量替代。
- 仓库中存在大量直接构造 SQL 的位置（字符串拼接）；如果为外部输入增加改动，请优先采用参数化查询或适当的校验与转义。

查询与调试技巧
- 若要定位某接口的实现，先打开 `app.py` 看蓝图挂载名，再在 `ops/` 目录下查找对应文件名。
- 要查看项目如何访问数据库，搜索 `mysqlMain(`，常见文件：`bin/runMySQL.py`, `lib/py/*`, `ops/*`。
- 若需临时在本地绕开远端服务，可在 `conf/config.ini` 中添加本地测试 URL/DB 节点并使用相同的节名。

修改/合并现有 AI 指南的策略
- 仓库当前没有 `.github/copilot-instructions.md`；若你希望合并已有公司/团队模板，请把模板贴到仓库根或 `.github/` 下并通知我来合并重要条目（例如 CI、认证信息、特定部署流程）。

如需我进行的下一步（请选择一项）
- 我可以把上面的文档写入仓库（已执行）。
- 或者你可以指出想扩充的区域（例如：典型请求/响应示例、常见 SQL fix 范例、蓝图模板），我将把它们加入并提交更新。

请检查上述内容是否满足你的期望，或告诉我需要补充/删除的部分（例如：补充某个 ops 子模块的实现细节）。