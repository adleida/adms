##Assist Of Adx

---

###职能

1. server 部署 存在形式独立

2. 提供向 dsp 注册身份 + 上传物料 + 注册 app 信息服务

---

###所需依赖

    Flask==0.10.1
    Flask-RESTful==0.3.2
    pyyaml==3.11
    pymongo==2.8
    jsonschema==2.4.0
    toolz==0.7.1
    ipdb==0.8

---

###程序快速启动

    git clone git@192.168.1.111:adms.git
    cd adms
    ./bin/core

---

###启动命令参数

    usage: adms [-h] [-v] [-b BIND] [-p PORT] [-d] [-l {info,warn,error}]

    use this command could decide to deploy your webserver on variety.

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         display version of adms
      -b BIND, --bind BIND  specify your server host bind
      -p PORT, --port PORT  specify your server port open
      -d, --debug           switch debug modern to scratch all log output
      -l {info,warn,error}, --loglevel {info,warn,error}
                            adjust more then default level of ouput

---

###数据模型

    dsp:
        _id: id
        name: name 
        burl: burl

        timestamp: timestamp

    adm:
        _id: _id
        did: did
        type: type
        data:
            app_url: app_url
            text: text
            img: img (changed by adx)

        media_id: media_id
        timestamp: timestamp

    media:
        _id: _id (sha1)
        filename: _id (sha1)
        approved: approved
        ref: ref
        timestamp: timestamp

---

###测试工具

1. 运行时测试

    import ipdb; ipdb.set_trace()

2. 单元测试

    pytest | tox

