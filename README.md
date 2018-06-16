# 起点爬虫

**用来爬取起点排行榜数据**

## 条件和依赖
Python 3.4+
[Scrapy](https://github.com/scrapy/scrapy)
[fonttools](https://github.com/fonttools/fonttools)
[Requests](https://github.com/requests/requests)

## 运行
参考[Scrapy](https://github.com/scrapy/scrapy)

### 爬作品排行榜
**默认爬月票榜**：
`scrapy crawl rank`
可指定参数`type`爬其他榜单，如：
`scrapy crawl rank -a type=collect` // 收藏榜
`type`参数取自网页url: `https://www.qidian.com/rank/collect?style=1`

### 爬粉丝打赏排行榜
**默认爬日榜**
`scrapy crawl fans-rank`
可指定参数`type`爬总榜：
`scrapy crawl fans-rank -a type=2` // 总榜
`type`参数取自网页url: `https://www.qidian.com/rank/fans?dateType=2`

