# Thank you follow me - 谢谢你关注我呀！

## 简介

这是一个用于自动给知乎里你的新关注者发送一条信息的后台服务。

技术栈什么的非常简单：

- 以前写的 `zhihu-py3` 用于获取知乎信息
- 用 `sqlite` 数据库保存老的关注者
- `daemon.py` 用于在 *unix 环境下创建 daemon proc

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

过程中需要验证码……如果你是在VPS上部署的话，你得想办法把 `captcha.gif` 文件从远程服务器弄到本地来查看验证码…… 

其实我更建议在本地用 `zhihu-py3` 生成 cookies 再弄到 VPS 上，这样就可以使用：

```bash
qqqfome -c /path/to/cookie -v init
```

来省略登录步骤。

如果一切正常的话，你会得到一个 sqlite 数据库文件。名字是 `<your-zhihu-id>.sqlite3`

### 启动

```bash
qqqfome -m $'I\'m {my_name}:\nThank you follow me.' -d start <your-zhihu-id>.sqlite3
```

（如果只是测试的话，可以去掉 `-d` 参数，让他在前台模式运行。）

`-m` 参数后跟需要发送的信息。注意，如果你在消息内部使用了转义字符，那么单引号前的`$`符号是必需的。

或者你可以将信息写在一个文件里，然后使用 `-M` 参数指定此文件。

两个都没有指定的话，默认的消息是：

```text
你好{your_name}，我是{my_name}，谢谢你关注我，你是我的第{follower_num}号关注者哟！

本消息由qqqfome项目自动发送。
项目地址：https://github.com/7sDream/qqqfome
{time}
```

程序支持的也就是例子里的这几个宏了……

## 查看Log

```bash
tail -f <your-zhihu-id>.sqlite3.log
```

默认的 log 文件名是 `<your-zhihu-id>.sqlite3.log`

还有一个是 `<your-zhihu-id>.sqlite3.pid` 这个文件不要删。

### 停止

如果不是后台模式，`Ctrl-C` 即可停止。

如果是 Daemon 模式，则：

```bash
qqqfome stop <sqlite_file_name>
```

## 文档

还没写，暂时用 `qqqfome -h` 凑合看吧。

```text
usage: qqqfome [-h] [-v] [-c FILE] [-p FILE] [-l FILE] [-t INTERVAL]
               [-m MESSAGE | -M FILE] [-s NUM] [-d]
               {init,start,stop} [file]

Thank-you-follow-me cli.

positional arguments:
  {init,start,stop}     command that you want exec
  file                  database file that you want run on.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         turn on this to print info
  -c FILE, --cookies FILE
                        provide cookies file if you have to skip login
  -p FILE, --pid-file FILE
                        pid file location
  -l FILE, --log-file FILE
                        log file location
  -t INTERVAL, --time INTERVAL
                        set the interval time
  -m MESSAGE, --message MESSAGE
                        the message that you want to send to your new follower
  -M FILE, --message-file FILE
                        the message that you want to send to your new follower
  -s NUM, --stop-at NUM
                        found NUM continuously old followers will stop pass
  -d, --daemon          work in daemon mode
```

## LICENSEE

MIT.
