##`cdproject/adms/handler/` 模块的细部流程

---

###dsp.py 模块

1. 提供简要`对dsp信息注册`操作方法

 - POST     (创建单条)      http POST   /v1/dsp/ < [data.json]
 - PUT      (变更单条)      http PUT    /v1/dsp/ [condition]=[value]
 - DELETE   (删减单条)      http DELETE /v1/dsp/ id=[value]
 - GET      (查询单条)      http GET    /v1/dsp/
 - GET      (查询多条)      http GET    /v1/dsp/<id>

2. request 返回码

 细部请参考配置文件 `cdproject/etc/main.yaml`

 - 200      (请求被接受)
 - 201      (请求内容已经被创建)

 - 400      (情求格式错误)
 - 401      (需要认证 该处未实现)
 - 404      (请求页面不存在)
 - 408      (请求超时)
 - 417      (请求发生冲突)
 - 500      (服务器内部错误)

---

###cre.py 模块 (app 信息注册)

1. 提供简要`对cre信息注册`操作方法

 - POST     (创建单条)      http POST   /v1/adm/ < [data.json]
 - DELETE   (删减单条)      http DELETE /v1/adm/ id=[value]
 - GET      (查询单条)      http GET    /v1/adm/
 - GET      (查询多条)      http GET    /v1/adm/<id>

2. request 返回码同上

---

###cre.py 模块 (物料信息以 base64 编码上传)

- 流程

 1. dsp 提供完整信息描述  其中 `img` 字段为真实物料的 base64 编码
 2. 我方取得 app 所有信息后处理  先将 `img` 解码并存入 gridfs  生成唯一 id
 3. 取得唯一 id 后拼凑为我方展示物料 url 并替换 `img` 字段
 4. 连同其他信息经过字段处理后入库 mongo
 5. 入口后更新物料关联 (`ref` `updated`)

- 测试

 - 录入文件
 import json
 `json.dump(data, file, indent=2)`

---

###cre.py 模块 (物料上传)

1. 上传流程

 1. 上传(或批量上传)图片至我方服务器
 2. 根据上传图片返回带有唯一 hash 值的图片展示 url
 3. dsp 方持有 url 拼凑完整 `cre信息` 完成注册
 4. 我方对未经审核通过的图片请求不予亦展示

2. 操作方法

 - 物料上传                http -f POST /v1/media/upload

---

###cre.py 模块 (物料展示)

- 操作方法

 - 物料展示                http GET     /v1/media/<id>

---

###cre.py 模块 (物料审核)

1. 审核流程

 1. 广告主 或 dsp 通过我方 api 接口 (直接界面上传或者 base64 连同 app 信息上传) 将物料置入我方 gridfs 中持久化
 2. 我方收到物料入库会做增加 [approvrd: False] 的处理
 3. 我方审核人员访问 url [ /v1/media/verify ] 发出 GET 请求向后台索取第一批物料 (数量可以在 /etc/main.yaml 中 [ init_limit ] 设定) 用以界面展示
 4. 我方审核人员点击按钮控件向后台 url [ /v1/media/verify/click ] 发出 POST 请求更变 approved 字段值 前台相应更变展示效果和属性字段
 5. 我方审核人员触发滚动下拉动作向后台 url [ /v1/media/verify/scroll ] 发出 GET 请求向后台索取第二批物料 (数量可以在 /etc/main.yaml 中 [scroll_limit ] 设定) 用以界面展示

2. 未解决的问题 (TODO)

 1. 现在采用单独 app 统一负责所有服务的受理 未来倘若服务上线 对外不应该暴露甚至开放审核模块的接口 (这里可以采用 [ 开放单独 app 负责审核模块 ] 或 [ 设定审核模块 url 传入参数才能访问进行保护 ] 两种做法)
 2. 审核模块还有多次滚动下拉通过 skip() 传值加载 未实现 因为每次倍率在配置文件写死 可以将倍数每次动态 +1 获取后台数据
