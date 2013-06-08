基于webqq协议和小i机器人的qq机器人。

你可以加QQ 2915573785 和这个机器人测试聊天。直接聊天，不用加#，如：

    你好

也可以把它加入到你管理的一个群里面，聊天的时候前面加个#，如：
    
    #你好

![](https://github.com/Shu-Ji/qqrobot/raw/master/img.jpg)

需要安装依赖库: pyquery requests.py

使用说明：

    将libqq.py中test函数中的qq和pwd修改成你的机器人qq账号。
    python libqq.py即可启动，如果需要输入验证码，请手动打开程序根目录下面的vc.jpg然后输入。
    如果安装了pil模块那么可以在libqq.py中_get_verifycode改成如下：
    
```python
    def _get_verifycode(self):
        '''获取验证码'''
        url = 'http://captcha.qq.com/getimage?aid=1003903&r=%s&uin=%s&vc_type=%s'
        url %= r(), self.qq, self.vc
        logging.debug('getting verifycode')
        img = n.get(url)
        open('vc.jpg', 'wb').write(img)
        import Image
        Image.open('vc.jpg').show()
        return img
```

另外一个基于webqq协议的qq客户端：https://github.com/Shu-Ji/coco

本程序Github地址：https://github.com/Shu-Ji/qqrobot
