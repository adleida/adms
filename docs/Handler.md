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
