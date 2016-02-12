# Thank you follow me - 谢谢你关注我呀！

## 简介

这是一个用于自动给知乎里你的新关注者发送一条信息的后台服务。

技术栈什么的非常简单：

- 以前写的 zhihu-py3 用于获取知乎信息
- 用 sqlite 数据库保存老的关注者
- daemon.py 用于在 *unix 环境下创建 daemon proc

## 安装

未发布到 pypi， 暂时使用源码安装吧。

### 下载源码包

```bash
git clone https://github.com/7sDream/qqqfome
cd qqqfome
```

### 简单测试

```bash
python3 -m unittest qqqfome.test
```

### 安装

```bash
sudo python3 setup.py install
```

### 创建工作目录

```bash
cd /path/that/you/want
mkdir qqqfome_work
cd qqqfome_work
```

### 初始化数据库

```bash
qqqfome -v init
```

然后根据提示登录知乎。

或者你使用过 zhihu-py3 的话，可以把 cookies 文件复制过来，省略登录步骤

```bash
qqqfome -c /path/to/cookie -v init
```

如果一切正常的话，你会得到一个 sqlite 数据库文件。

### 启动

```bash
qqqfome -m "Thank you follow me." -d start <sqlite_file_name> 
```

（如果只是测试的话，可以去掉 -d 参数，让他在前台模式运行。）

-m 参数后跟需要发送的信息。

或者你可以将信息写在一个文件里，然后使用 `-M` 参数指定此文件。

### 停止

如果不是后台模式，Ctrl-C 即可停止。

如果是 Daemon 模式，则：

```bash
qqqfome stop <sqlite_file_name>
```

## 文档

还没写，暂时用 `qqqfome -h` 凑合看吧。

## LICENSEE

MIT.
