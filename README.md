# 0aK

> The oak is a living legend representing all that is true, wholesome, stable, and noble. When you are in need of stability and strength in your life – envision the oak in your minds eye. Picture yourself drawing into its endless energy waves. Soon, you will find yourself sharing in its power.



## Log

**V1.0 : first commit (a semi-automatic version)**



## Features

[demo](https://demo.0akarma.com/)

- Nice design with dark & light themes.

![](https://ws1.sinaimg.cn/large/006tNc79ly1g29i0ok6h4j31f40u07wk.jpg)

![](https://ws4.sinaimg.cn/large/006tNc79ly1g29i3mm5h1j31f10u07wk.jpg)

- You can create any category on your own.
- The management page now can only create categories and articles.

![](https://ws3.sinaimg.cn/large/006tNc79ly1g29i502ygpj31eu0u0agw.jpg)

- The html style on the article page.

![](https://ws4.sinaimg.cn/large/006tNc79ly1g29ievx2qyj31f30u0jyj.jpg)

## How to use

1. Docker (recommend)

   You can just use commands as follow.

   ```bash
   git clone https://github.com/akkayin/0aK.git
   cd 0aK
   docker build -t 0aK/blog:v1 .
   docker run -tid --name 0ak -p 80:80 0aK/blog:v1 /bin/bash
   ```

   or you just use docker-compose, if you have installed it before.

   `docker-compose up`

2. wsgi

   ```bash
   git clone https://github.com/akkayin/0aK.git
   cd 0aK
   pip install -r requirements.txt
   python wsgi.py
   ```



## Summary

If you like `oak`, please fork it.

Or if you have some problem with it, please commit an issue and let me know.

My project is not perfect enough cause you can not get along well with it if you do not have any programming experience:(

More Information about this project, you can view it on my [blog](https://www.0akarma.com/0ak-blog.html)

## 