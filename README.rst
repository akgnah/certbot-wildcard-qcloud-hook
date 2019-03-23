certbot-wildcard-qcloud-hook
===============================

Let’s Encrypt 在 2018 年推出了 wildcard 证书，申请或更新 wildcard 证书只能使用 dns-01 的方式来检验域名所有权，操作略有麻烦。
如果你的域名使用腾讯云 DNS （dnspod）解析，该工具可帮助你自动化该过程，特别是当申请多域名证书（SAN 证书）时，将会明显感受到便利。

安装
------

1. 安装 Certbot
^^^^^^^^^^^^^^^^^^

请访问 https://certbot.eff.org/ 参照说明安装。

2. 安装依赖
^^^^^^^^^^^^^^

.. code-block:: bash

   $ pip install requests

3. 下载本工具
^^^^^^^^^^^^^^

.. code-block:: bash

   $ git https://github.com/akgnah/certbot-wildcard-qcloud-hook
   $ cd certbot-wildcard-qcloud-hook
   $ chmod +x qcloud-dns.py

程序在 Ubuntu 18.04 上（Certbot 版本为 0.31.0），Python2.7 和 3.6 测试通过。

使用
------

1. 申请腾讯云 API
^^^^^^^^^^^^^^^^^^^

请访问 https://console.cloud.tencent.com/cam/capi 申请，并修改 qcloud-dns.py 中的 secret_id 和 secret_key。

2. 申请证书
^^^^^^^^^^^^^^

请把 *.example.com 换成你的域名，把 /path/to/qcloud-dns.py 换成 qcloud-dns.py 实际路径，先测试一下是否有错误：

.. code-block:: bash

   $ certbot certonly -d *.example.com --manual --preferred-challenges dns --manual-auth-hook "/path/to/qcloud-dns.py add" --manual-cleanup-hook "/path/to/qcloud-dns.py del" --dry-run

若没有错误发生，我们来实际申请（去掉了 --dry-run 参数）

.. code-block:: bash

   $ certbot certonly -d *.example.com --manual --preferred-challenges dns --manual-auth-hook "/path/to/qcloud-dns.py add" --manual-cleanup-hook "/path/to/qcloud-dns.py del"

如果你需要申请多域名证书（SAN 证书），输入多个 -d 参数即可，它们会合并在一张证书中。如下所示将会为 example.com 和 *.example.com 同时申请证书：

.. code-block:: bash

   $ certbot certonly -d example.com -d *.example.com --manual --preferred-challenges dns --manual-auth-hook "/path/to/qcloud-dns.py add" --manual-cleanup-hook "/path/to/qcloud-dns.py del"

3. 更新证书
^^^^^^^^^^^^^

Let’s Encrypt 的证书有效期是 90 天，当有效期小于 30 天时可申请更新证书。

更新符合有效期要求的全部证书：

.. code-block:: bash

   $ certbot renew --manual --preferred-challenges dns --manual-auth-hook "/path/to/qcloud-dns.py add" --manual-cleanup-hook "/path/to/qcloud-dns.py del"

更新某一域名的证书：

.. code-block:: bash

   $ certbot renew --cert-name example.com --manual --preferred-challenges dns --manual-auth-hook "/path/to/qcloud-dns.py add" --manual-cleanup-hook "/path/to/qcloud-dns.py del"

你可使用 crontab -e 命令把它加进定时作业中。

杂项
------

拓展阅读
^^^^^^^^^^^

`如何免费的让网站启用 HTTPS | | 酷 壳 - CoolShell <https://coolshell.cn/articles/18094.html>`_ 

相似项目
^^^^^^^^^^

`certbot-letencrypt-wildcardcertificates-alydns-au <https://github.com/ywdblog/certbot-letencrypt-wildcardcertificates-alydns-au>`_ 
