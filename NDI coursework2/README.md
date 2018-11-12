# pkyx

pkyx是基于Flask开发的一个比较网站，灵感来自于[VSChart](http://vschart.com)。

demo: [pkyx](http://45.78.53.13)

[10天开发一个网站](http://tonnie17.github.io/2015/10/11/pkyx/)

## 安装依赖

`
pip install -r requirement.txt
`


## 配置文件

```
app/config.py
```

## 运行

`
gunicorn wsgi:app -c gunicorn.conf
`

or

`
python manage.py
`
