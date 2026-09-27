# 寺庙修缮募捐功德纪要系统 · 寺庙殿堂与功德主登记接口

## 这个仓库是什么

寺院要修缮殿堂。系统先把每座寺庙、每间待修殿堂的病害与修缮方案登记下来，再开现场会、转写录音、由大模型生成募捐文案，最后把功德纪要邮寄给信众。功德主在页面上留名、留邮箱、写随喜金额；月底客堂照这份名单群发纪要邮件，功德碑也照它排名。

这里裁剪出来的只有「寺庙 / 殿堂 / 功德主登记」这一层 REST 接口和它底下的 ORM。录音转写、AI 文案生成、纪要渲染、邮件发送都不在范围内，不要去找它们。上游入口 `backend/main.py` 也没有携带——它做的事就是建表、挂 CORS、把三个路由 `app.include_router(router, prefix="/api")`。测试里自己建一个 `FastAPI()` 把这两个 router 挂上去就行，前缀按 `/api` 来，跟线上一致：

```python
app = FastAPI()
app.include_router(temples.router, prefix="/api")
app.include_router(donors.router, prefix="/api")
```

## 目录

- `backend/config.py` — 配置项，pydantic-settings，import 时从环境变量和 `.env` 读。
- `backend/database.py` — `engine` / `SessionLocal` / `Base` / `get_db`。`get_db` 是 FastAPI 依赖，一个请求一个 Session。
- `backend/models.py` — 五张表的 ORM 模型：`temples` / `halls` / `meetings` / `dialogue_turns` / `donors`。
- `backend/schemas.py` — 请求响应模型，pydantic v2。
- `backend/api/temples.py` — 挂 `/api/temples`，寺庙与殿堂。
- `backend/api/donors.py` — 挂 `/api/donors`，功德主登记。

`backend` 和 `backend.api` 都带空的 `__init__.py`，是常规包。验证命令必须从仓库根目录、用 `-m` 的形式跑，这样仓库根才会进 `sys.path`，`from backend.api import temples, donors` 才解析得到。

## 运行环境

寺院客堂的内网机器，离线。`~/venvs/gsb-temple` 里只有 `requirements-task.txt` 列出来的包。**没有 uvicorn，也不需要起服务**：用 `fastapi.testclient.TestClient` 直接打接口，别去 bind 端口。**没有 `email-validator`**，所以 pydantic 的 `EmailStr` 一 import 就报错，邮箱校验自己写正则。

库是 SQLite。`DATABASE_URL` 默认 `sqlite:///./merit_record.db`，`backend/database.py` 在 import 阶段就 `create_engine`。`create_engine` 本身不落文件，第一次连接才落——所以测试只要不碰默认 engine（自己建一个指向 `tmp_path` 的 engine、`Base.metadata.create_all` 之后用 `app.dependency_overrides[get_db]` 顶掉依赖），仓库工作目录里就不会多出 `merit_record.db`。跑完整套测试之后工作树必须干净：不留 `.db`、不留 `output/`、不改 `README.md` 以外的既有文件；也不要让某台机器上的 `.env` 决定测试结果。

`schemas.py` 里那几个 `class Config: orm_mode = True` 是 pydantic v1 的旧写法，v2 会自动映射成 `from_attributes`，只发一条 UserWarning，接口照常工作。这次不要求改它，也别把 warning 升级成 error。

## 接口清单（前端与月底群发脚本的硬约定）

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/temples/` | 登记寺庙 |
| GET | `/api/temples/?skip=&limit=` | 寺庙列表 |
| GET | `/api/temples/{temple_id}` | 寺庙详情 |
| POST | `/api/temples/{temple_id}/halls` | 在某座寺庙下登记殿堂 |
| GET | `/api/temples/{temple_id}/halls` | 某座寺庙的殿堂列表 |
| GET | `/api/temples/halls/{hall_id}` | 殿堂详情 |
| PUT | `/api/temples/halls/{hall_id}` | 改殿堂 |
| POST | `/api/donors/` | 功德主登记 |
| GET | `/api/donors/?skip=&limit=` | 功德主列表 |
| GET | `/api/donors/{donor_id}` | 功德主详情 |

路径、方法、响应模型的字段名都是前端写死的，**不能改**。可以新增路由、新增字段、新增 schema。

## 数据形状

- `Temple`：`id, name, location, description, created_at`
- `Hall`：`id, temple_id, name, description, damage_details, repair_plan, estimated_cost, created_at`
- `Donor`：`id, name, email, phone, amount, blessing_content, created_at`

`damage_details` 与 `repair_plan` 是 JSON 对象，形如 `{"木构腐朽": "大殿明间两根金柱柱脚糟朽", "彩绘剥落": "梁枋彩画起甲空鼓"}`。`estimated_cost` 是中文字符串，形如 `"80万元"`。`Donor.amount` 同样是字符串，形如 `"壹仟元"`、`"￥5,000"`、`"随喜"`。这三处的字符串存法，下游（纪要渲染、功德碑排名、群发脚本）都在按现状解析，**这次不改它们怎么存**；这次改的是接口对它们的校验与更新行为。

## 已经定死的口径

**K1 `created_at` 必须自带时区信息。** 该列由数据库端 `server_default` 生成，类型是 `DateTime(timezone=True)`，但 SQLite 的 `CURRENT_TIMESTAMP` 落下来是不带时区的 UTC 墙上时间，响应里就成了 `"2026-09-26T13:15:48"` 这种裸串。前端 `new Date(...)` 把它当本地时间解析，功德榜上印出来的登记时间比客堂墙上挂钟早 8 小时。修完之后：响应里的 `created_at` 必须能让读的人一眼看出是哪个时区的几点；同一条记录在列表接口和详情接口给出的时间必须一致；老库里已经存进去的裸时间行必须还读得出来，不许因为改口径就 500。

**K2 殿堂必须挂在一座真实存在的寺庙下。** 任何写入路径都不得留下 `temple_id` 指向不存在寺庙的孤儿殿堂。

**K3 存在性答复口径一致。** `GET /api/temples/{temple_id}` 和 `GET /api/temples/{temple_id}/halls` 对「这座寺庙存不存在」必须给同一种答复。

**K4 部分更新不得抹空。** `PUT /api/temples/halls/{hall_id}` 收到只带部分字段的请求时，没带的字段保持原值。前端那个「修改预估修缮费用」的弹框只提交 `name` 和 `estimated_cost` 两个字段，现在提交一次，病害详情和修缮方案就全被写成 `null` 了。

**K5 功德主邮箱必须是能寄到的形状。** 这是月底群发的收件地址。空串、只有空白、`abc` 这种没有 `@` 的都不许进库。同一个邮箱重复登记，客堂要能立刻知道，不许默默地存下两条——现在一个人连点三次「登记」就是三条，群发时一人收三封。

## 需要你自己拿主意的口径

上面只说了「必须一致 / 不得抹空 / 必须能寄到」，具体怎么落地有好几种做法，结论不一样。每种都选一个，把理由写进下面这一节，评审看这里：

- **时间口径**：库里改存带时区的 UTC、还是保持库里裸 UTC 只在响应层补 `+00:00`、还是干脆按 Asia/Shanghai 存本地时间再补 `+08:00`。三种都能让前端显示对，代价差在老数据可读性和跨时区部署。
- **部分更新语义**：把 `PUT` 改成真部分更新（只写请求里出现过的字段）、保持 `PUT` 的全量语义但把可空字段变必填、还是另开一个 `PATCH` 而让 `PUT` 不动。前端现在发的是 `PUT`，你选的方案要说清楚前端跟不跟着改。
- **请求体 `temple_id` 与路径 `{temple_id}` 不一致**：`POST /api/temples/1/halls` 带 `{"temple_id": 9999, ...}` 时，报 422、以路径为准并忽略请求体、还是以请求体为准。现在是不声不响地以路径为准，请求体那个值直接被丢掉。
- **重复邮箱**：409 拒绝、按邮箱 upsert 覆盖旧记录、还是允许重复但在响应里标出来让客堂自己合并。选哪种要说清楚月底群发脚本那边要不要跟着改。
- **邮箱校验的严格程度**：只查 `本地部分@域名` 的形状，还是连域名里有没有点、有没有连续点号也管。管得越严，越容易把寺院里那种手填的 `xxx@foo` 内网地址挡在门外。

### 本次做题人填写

（把你的取舍和理由写在这里。）