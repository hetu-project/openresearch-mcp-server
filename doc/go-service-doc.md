# 接口文档

# 服务器地址

```jsx
**测试服务器：
https://test.nftkash.xyz/neo4j**
```

# 论文类

## 查询搜索论文

```jsx
GET  /papers

示例:
GET /papers
GET /papers?id=1eb1aefe-5c8f-5224-8180-61a4ed18d4fe
GET /papers?title=Web3.0 Data Infrastructure: Challenges and Opportunities
GET /papers?keyword=机器学习&author=wang hua&year=2023
GET /papers?venue=arxiv
//多关键词查询：
GET /neo4j/v1/papers?keywords=blockchain,ai,nlp
GET /neo4j/v1/papers?keywords=blockchain&keywords=ai&keywords=nlp

//header
Authorization: Bearer <ACCESS_TOKEN>
（请求头如果不加，is_favorited_by_user和is_liked_by_user都是false，还是能正常调用这个接口）
（如果加了请求头，返回用户与论文交互的信息，is_favorited_by_user和is_liked_by_user）

//request 
{
	"title": 标题,    // optional
	"keywords": 关键词,    // optional
	"author": 作者,    // optional
	"year": 年,    // optional
	"doi": 论文doi,    // optional
	"url": 论文url,    // optional
	"id": 论文id,    // optional
	"limit": 结果数量，默认20    // optional
}

// reponse
{
  "count": 1,
  "papers": [
    {
      "abstract": "The development of network has brought subject information construction unprecedented challenges and opportunities in higher education institutions. Web3.0 is a recently proposed concept of Internet-based service. This paper introduces the ideas of Web3.0 to subject information integration. By analyzing the current subject information resources and subject information integration approaches in higher education institutions, a design of subject information integration system is brought forward in this paper. This design can give an efficient reference to subject information integration in the context of Web3.0.",
      "authors": [
        {
          "id": "940c720f-a20d-5315-853f-733dbca697b8",
          "name": "Niu Li"
        },
        {
          "id": "4ebbdc82-a713-56f8-8428-df4eeac1b27d",
          "name": "Han Xiaoting"
        }
      ],
      "citations": 9,
      "doi": "10.1109/ICINDMA.2010.5538341",
      "id": "1eb1aefe-5c8f-5224-8180-61a4ed18d4fe",
      "keywords": [
        "Industrial economics",
        "Construction industry",
        "User-generated content",
        "Web sites",
        "Databases",
        "IP networks",
        "Information analysis",
        "Intelligent networks",
        "Web and internet services",
        "Artificial intelligence"
      ],
      "published_at": "2010-05-01T08:00:00+08:00",
      "title": "Subject information integration of higher education institutions in the context of Web3.0",
      "url": "https://ieeexplore.ieee.org/document/5538341",
      "venue_name": "2010 The 2nd International Conference on Industrial Mechatronics and Automation"
	    "is_favorited_by_user": false,   // 是否被用户收藏
      "is_liked_by_user": false,  // 是否被点赞
      "likes_count": 0,  // 点赞数量
      "img_url" : "https://". // 论文pdf首页缩略图
    }
  ]
}

```

## 创建论文

```jsx
POST /papers/create

//request 
{
  "paper": {
    "title": "基于深度学习的知识图谱构建方法",
    "abstract": "本文提出了一种基于深度学习的知识图谱构建方法...",
    "doi": "10.1234/abcd.2023.54321",
    "url": "https://example.com/papers/54321",
		"citations": 0,
		"references_count": 0,
    "keywords": ["深度学习", "知识图谱", "自然语言处理"]
  },
  "authors": [
    {
      "name": "张伟",
      "affiliation": "浙江大学计算机学院"
    },
    {
      "name": "王芳",
      "affiliation": "复旦大学计算机科学技术学院"
    }
  ]
}

//reponse
{
  "message": "paper created successfully",
  "paper": {
    "id": "7f6e5d4c-3b2a-1d0e-9f8g-7h6i5j4k3l2m",
    "title": "基于深度学习的知识图谱构建方法",
    "abstract": "本文提出了一种基于深度学习的知识图谱构建方法...",
    "doi": "10.1234/abcd.2023.54321",
    "url": "https://example.com/papers/54321",
    "citations": 0,
    "references_count": 0,
    "keywords": ["深度学习", "知识图谱", "自然语言处理"]
  }
}
```

## **获取论文引用关系**

```jsx
GET /papers/:id/citations

//request
{
	"id": 论文id
}

//reponse

{
  "paper_id": "8f7e6d5c-4b3a-2d1e-0f9g-8h7i6j5k4l3m",
  "title": "机器学习在自然语言处理中的应用",
  "url": "https://example.com/papers/12345",
  "doi": "10.1234/abcd.2023.12345",
  "outgoing_citations_count": 45, // 论文引用了多少篇其他论文
  "incoming_citations_count": 125, // 有多少篇论文引用了当前论文
  "total_citations_count": 170,  // 包含引用和被引用
  "cited_papers": [  // 当前论文引用的所有论文的信息
    {
      "id": "6d5c4b3a-2d1e-0f9g-8h7i-6j5k4l3m2n1o",
      "title": "深度学习在自然语言处理中的应用综述",
      "doi": "10.1234/abcd.2022.11111",
      "url": "https://example.com/papers/11111",
      "citations": 320,
      "keywords": ["深度学习", "自然语言处理", "综述"],
      "cited_at": "2023-02-10T00:00:00Z"
    }
  ],
  "citing_papers": [    // 引用当前论文的所有论文的信息
    {
      "id": "5c4b3a2d-1e0f-9g8h-7i6j-5k4l3m2n1o0p",
      "title": "基于Transformer的情感分析模型",
      "doi": "10.1234/abcd.2023.22222",
      "url": "https://example.com/papers/22222",
      "citations": 45,
      "keywords": ["Transformer", "情感分析", "自然语言处理"],
      "cited_at": "2023-04-15T00:00:00Z"
    }
  ]
}
```

## **获取论文推荐**

```jsx
GET /papers/:id/recommendations

//request
{
	"id": 论文id
}

//reponse
{
  "recommendations": [
    {
      "id": "4b3a2d1e-0f9g-8h7i-6j5k-4l3m2n1o0p9q",
      "title": "自然语言处理中的注意力机制研究",
      "citations": 156,
      "relevance_score": 3
    },
    {
      "id": "3a2d1e0f-9g8h-7i6j-5k4l-3m2n1o0p9q8r",
      "title": "基于BERT的文本分类方法",
      "citations": 98,
      "relevance_score": 2
    }
  ],
  "count": 2
}
```

## **获取热门论文**

```jsx
GET /papers/trending

示例：
GET /papers/trending?time=month&limit=5

// request
{ 
	"time": "week" or "month" or "year"，   // 默认month
	"limit": 5  // 默认20
}

//reponse
{
  "trending_papers": [
    {
      "id": "2d1e0f9g-8h7i-6j5k-4l3m-2n1o0p9q8r7s",
      "title": "大型语言模型在医疗领域的应用",
      "abstract": "本文探讨了大型语言模型在医疗诊断、医学文献分析等领域的应用...",
      "doi": "10.1234/abcd.2023.33333",
      "url": "https://example.com/papers/33333",
      "citations": 78,
      "published_at": "2023-05-05T00:00:00Z",
      "published_year": 2023,
      "keywords": ["大型语言模型", "医疗", "人工智能"],
      "authors": ["李华", "张强"],
      "popularity_score": 9.82
    }
  ],
  "count": 1,
  "time_window": "month"
}
```

## 获取热门话题

```jsx
GET /papers/keywords/top

示例：

// reponse 
{
  "count": 6,
  "keywords": [
    {
      "keyword": "Blockchains",
      "paper_count": 164
    },
    {
      "keyword": "Smart contracts",
      "paper_count": 129
    },
    {
      "keyword": "Privacy",
      "paper_count": 59
    },
    {
      "keyword": "Security",
      "paper_count": 55
    },
    {
      "keyword": "Decentralized applications",
      "paper_count": 53
    },
    {
      "keyword": "Semantic Web",
      "paper_count": 47
    }
  ]
}
```

## 获取全部话题

```jsx
GET /papers/keywords/all

//reponse
{
  "count": 723,
  "keywords": [
    {
      "keyword": "Blockchains",
      "paper_count": 164
    },
    {
      "keyword": "Smart contracts",
      "paper_count": 129
    },
    {
      "keyword": "Privacy",
      "paper_count": 59
    },
    {
      "keyword": "Security",
      "paper_count": 55
    },
    {
      "keyword": "Decentralized applications",
      "paper_count": 53
    },
    {
      "keyword": "Semantic Web",
      "paper_count": 47
    },
    {
      "keyword": "Scalability",
      "paper_count": 42
    },
    {
      "keyword": "cs.CR",
      "paper_count": 39
    }
  ]
}
```

## 点赞论文

```jsx
POST /papers/:id/like

示例：
POST /papers/418fa446-f23a-56df-8c66-2629ea877ffd/like

//header
Authorization: Bearer <ACCESS_TOKEN>

//request
{
	"id": 论文id
}

//reponse
{
	"message": "paper like status updated",
	"favorite":{
		"id": 1  
		"paper_id": "418fa446-f23a-56df-8c66-2629ea877ffd" //论文id
		"user_id": 1 // 用户id
		"favorited_at": "2025-05-28T12:20:36.26866+08:00" // 首次点赞时间
		"status": true or false  // true为以点赞，false为取消点赞/未点赞
		"updated_at": "2025-05-28T14:25:26.368345+08:00" // 更新时间
		
	}
}
```

## 收藏论文

```jsx
POST /papers/:id/favorite

示例：
POST /papers/418fa446-f23a-56df-8c66-2629ea877ffd/favorite

//header
Authorization: Bearer <ACCESS_TOKEN>

//request
{
	"id": 论文id
}

//reponse
{
	"message": "paper favorite status updated",
	"favorite":{
		"id": 1  
		"paper_id": "418fa446-f23a-56df-8c66-2629ea877ffd" //论文id
		"user_id": 1 // 用户id
		"favorited_at": "2025-05-28T12:20:36.26866+08:00" // 首次收藏时间
		"status": true or false  // true为以收藏，false为取消收藏/未收藏
		"updated_at": "2025-05-28T14:25:26.368345+08:00" // 更新时间
		
	}
}
```

## 查看用户当前收藏的论文

```jsx
GET /papers/favorites

//header
Authorization: Bearer <ACCESS_TOKEN>

//reponse
{
	"count": 1,
	"papers": {
			[
				"id" : "418fa446-f23a-56df-8c66-2629ea877ffd",
				"title": 
				"abstract":
				"published_at":
				"doi":
				"url":
				"citations":
				"references_count":
				"venue_id":
				"likes_count": 5
				"is_liked_by_user": true or false,
				"is_favorited_by_user": true or false,
			],
			[
			
			]
	}
}
```

# 作者类

## **搜索作者**

```jsx
GET /authors

示例：
GET /authors?id=1eb1aefe-5c8f-5224-8180-61a4ed1831za
GET /authors?name=张三&affiliation=北京大学

//request
{
	"id": 作者id,   // optional
	"name": 作者名字，// optional
	"affiliation": 作者机构,// optional
	"interest": 研究兴趣,// optional
}

//reponse
{
  "authors": [
    {
      "affiliation": "School of Economics and Management, Beihang University, Beijing, China",
      "citation_count": 0,
      "coauthors": [ // 合作过的作者
        {
          "affiliation": "School of Economics and Management, Beihang University, Beijing, China",
          "citation_count": 0,
          "collaboration_count": 1,
          "id": "940c720f-a20d-5315-853f-733dbca697b8",
          "name": "Niu Li"
        }
      ],
      "email": "",
      "h_index": 0,
      "id": "4ebbdc82-a713-56f8-8428-df4eeac1b27d",
      "name": "Han Xiaoting",
      "paper_count": 1,
      "research_interests": null
    }
  ],
  "count": 1,
  "params": {
    "include_coauthors": true,
    "limit": 10,
    "name": "Han Xiaoting"
  }
}
```

## 获取作者发表的所有论文

```jsx
GET /authors/:id/papers

示例：
GET. /authors/4ebbdc82-a713-56f8-8428-df4eeac1b27d/papers

//request
{
	"id": 作者id
}

//reponse
{
  "count": 1,
  "papers": [
    {
      "author_order": 1,
      "id": "1eb1aefe-5c8f-5224-8180-61a4ed18d4fe",
      "is_corresponding": true,
      "published_at": "2010-05-01T08:00:00+08:00",
      "title": "Subject information integration of higher education institutions in the context of Web3.0"
    }
  ]
}
```

## **获取合作者列表**

```jsx
GET /authors/:id/coauthors

示例：
GET. /authors/4ebbdc82-a713-56f8-8428-df4eeac1b27d/coauthors

//request
{
	"id": 作者id
}

//reponse
{
  "author_id": "4ebbdc82-a713-56f8-8428-df4eeac1b27d",
  "coauthors": [
    {
      "affiliation": "School of Economics and Management, Beihang University, Beijing, China",
      "citation_count": 0,
      "collaboration_count": 1,
      "id": "940c720f-a20d-5315-853f-733dbca697b8",
      "name": "Niu Li"
    }
  ],
  "count": 1
}
```

## 获取两位作者共同发表的论文

```jsx
GET /authors/:id/co-authored-papers

示例：
GET /authors/4ebbdc82-a713-56f8-8428-df4eeac1b27d/co-authored-papers?coauthor_id=940c720f-a20d-5315-853f-733dbca697b8

//request
{
	"id": 第一位作者ID,
	"coauthor_id": 第二位作者ID
}

//reponse
{
  "author_id1": "4ebbdc82-a713-56f8-8428-df4eeac1b27d",
  "author_id2": "940c720f-a20d-5315-853f-733dbca697b8",
  "count": 1,
  "papers": [
    {
      "abstract": "The development of network has brought subject information construction unprecedented challenges and opportunities in higher education institutions. Web3.0 is a recently proposed concept of Internet-based service. This paper introduces the ideas of Web3.0 to subject information integration. By analyzing the current subject information resources and subject information integration approaches in higher education institutions, a design of subject information integration system is brought forward in this paper. This design can give an efficient reference to subject information integration in the context of Web3.0.",
      "citations": 9,
      "created_at": "2025-05-26T20:32:27+08:00",
      "doi": "10.1109/ICINDMA.2010.5538341",
      "id": "1eb1aefe-5c8f-5224-8180-61a4ed18d4fe",
      "keywords": [
        "Industrial economics",
        "Construction industry",
        "User-generated content",
        "Web sites",
        "Databases",
        "IP networks",
        "Information analysis",
        "Intelligent networks",
        "Web and internet services",
        "Artificial intelligence"
      ],
      "published_at": "2010-05-01T08:00:00+08:00",
      "references_count": 3,
      "title": "Subject information integration of higher education institutions in the context of Web3.0",
      "updated_at": "2025-05-26T20:32:27+08:00",
      "url": "https://ieeexplore.ieee.org/document/5538341",
      "venue_id": "ieee",
      "venue_name": "2010 The 2nd International Conference on Industrial Mechatronics and Automation"
    }
  ]
}
```

# 图谱类

## 获取论文节点图谱

```jsx
GET /network/paper/:id

示例：
GET /network/paper/1eb1aefe-5c8f-5224-8180-61a4ed18d4fe?depth=2

//request
{
	"id": 论文id,
	"depth": 图谱深度，   // optional 默认1 (2会增加与论文相似的其他论文，类型为similar_topic)
	“max_nodes”: 节点数量， // optional 默认20
}

//reponse
{
  "paper_id": "8f7e6d5c-4b3a-2d1e-0f9g-8h7i6j5k4l3m",
  "depth": 1,
  "max_nodes": 20,
  "graph": {
    "nodes": [ // nodes数组第一个元素是中心节点
      {
        "id": "1eb1aefe-5c8f-5224-8180-61a4ed18d4fe",
        "type": "paper",
        "label": "Subject information integration of higher education institutions in the context of Web3.0",
        "properties": {
          "abstract": "...",
          "citations": 9,
          "published_at": "2010-05-01T08:00:00+08:00"
        }
      },
      {
        "id": "5c3bdc38-5d50-5f62-846f-1ebb7e25cd2d",
        "type": "paper",
        "label": "A Systematic Literature Review of Decentralized Applications in Web3: Identifying Challenges and Opportunities for Blockchain Developers",
        "properties": {
          "citations": 6,
          "rel_type": "cited"
        }
      }
    ],
    "edges": [
      {
        "source": "1eb1aefe-5c8f-5224-8180-61a4ed18d4fe",
        "target": "a4c1789c-d21c-58ff-854f-c69a73f635db",
        "type": "cites",
        "weight": 0.7,
        "properties": {
          "context": "Academic Research"
        }
      },
			{
        "source": "1eb1aefe-5c8f-5224-8180-61a4ed18d4fe",
        "target": "47b9e19a-2b76-5329-8c11-d1dd6414907e",
        "type": "similar_topic",
        "weight": 0.6,
        "properties": {
          "common_keywords": 1,
          "keywords": [
            "Web sites"
          ]
        }
      }
    ]
  }
}
```

## 获取作者节点图谱

```jsx
GET /network/author/:id

示例：
GET /network/author/4ebbdc82-a713-56f8-8428-df4eeac1b27d?depth=1

//request
{
	"id": 作者id,
	"depth": 图谱深度，   // optional 默认1 (2会增加与论文相似的其他论文，类型为similar_topic)
	“max_nodes”: 节点数量， // optional 默认20
}

//reponse
{
  "author_id": "4ebbdc82-a713-56f8-8428-df4eeac1b27d",
  "depth": 1,
  "graph": {
    "nodes": [
      {
        "id": "4ebbdc82-a713-56f8-8428-df4eeac1b27d",
        "type": "author",
        "label": "Han Xiaoting",
        "properties": {
          "affiliation": "School of Economics and Management, Beihang University, Beijing, China",
          "citation_count": 0
        }
      },
      {
        "id": "940c720f-a20d-5315-853f-733dbca697b8",
        "type": "author",
        "label": "Niu Li",
        "properties": {
          "affiliation": "School of Economics and Management, Beihang University, Beijing, China",
          "citation_count": 0
        }
      }
    ],
    "edges": [
      {
        "source": "4ebbdc82-a713-56f8-8428-df4eeac1b27d",
        "target": "940c720f-a20d-5315-853f-733dbca697b8",
        "type": "collaborates",
        "weight": 1,
        "properties": {
          "papers_count": 1
        }
      }
    ]
  },
  "max_nodes": 20
}
```

# 用户类

## 用户添加固定标签

```jsx
POST /papers/keywords/pinned

//header
Authorization: Bearer <ACCESS_TOKEN>

//request
{
	"keyword": "blockchain"
}

//reponse
{
	"message":"pinned keyword added successfully",
	"pinned_keyword":{
		"id":1,
		"user_id":"1",
		"keyword":"blockchain",
		"created_at":"2025-05-28T19:25:55.547107+08:00",
		"updated_at":"2025-05-28T19:25:55.547107+08:00"
	}
}
```

## 获取用户固定的标签

```jsx
GET /papers/keywords/pinned

//header
Authorization: Bearer <ACCESS_TOKEN>

//reponse
{
	"count":2,
	"pinned_keywords":[
		{
			"id":2,
			"user_id":"1",
			"keyword":"web3",
			"created_at":"2025-05-28T19:28:17.879911+08:00",
			"updated_at":"2025-05-28T19:28:17.879911+08:00"
		},
		{
			"id":1,
			"user_id":"1",
			"keyword":"blockchain",
			"created_at":"2025-05-28T19:28:17.879911+08:00",
			"updated_at":"2025-05-28T19:28:17.879911+08:00"
		}
	]
}
```

## 删除指定的某个标签

```jsx
DELETE /papers/keywords/pinned/:keyword

示例：
/papers/keywords/pinned/web3

//header
Authorization: Bearer <ACCESS_TOKEN>

//reponse
{
	"message":"pinned keyword removed successfully"
}
```

## 删除所有标签

```jsx
DELETE /papers/keywords/pinned

//header
Authorization: Bearer <ACCESS_TOKEN>

//reponse
{
	"message":"all pinned keywords cleared successfully"
}
```

## 获取首页全局评论与讨论页面数据

```jsx
GET /papers/comments/recent

示例：
GET /papers/comments/recent?limit=30

//request
{
		"limit": 20     // optional 不传limit则默认30，最大为50（暂定）
}

//reponse
{
  "comments": [
    {
      "id": 1,
      "user_id": "1",
      "paper_id": "123",
      "paper_title": "示例论文",
      "content": "这是一条评论",
      "created_at": "2025-05-29T12:00:00Z",
      "updated_at": "2025-05-29T12:00:00Z",
      "replies": [   // 评论里的回复
        {
          "id": 101,
          "comment_id": 1,
          "user_id": "1",
          "content": "这是一条回复",
          "created_at": "2025-05-29T12:30:00Z",
          "updated_at": "2025-05-29T12:30:00Z"
        }
      ],
      "replies_count": 1
    }
  ],
  "count": 1
}
```

## 获取指定论文的评论

```jsx
GET /papers/:id/comments

示例：
GET /papers/2880a9c9-ff10-52fe-88c0-a18c81550007/comments?page=1&page_size=10

//request
{
	 "id" : 论文id,
	 "page": 页,   // optional.  默认1
	 "page_size": 数量,  // optional. 默认10
}

//reponse
{
  "comments": [
    {
      "content": "这是一条测试评论",
      "created_at": "2025-05-29T15:06:53.544008+08:00",
      "id": 2,  // 评论id
      "paper_id": "2880a9c9-ff10-52fe-88c0-a18c81550007",
      "paper_title": "A Novel Smart Healthcare Design, Simulation, and Implementation Using Healthcare 4.0 Processes",
      "replies": [. // 评论下的回复内容
        {
          "comment_id": 2,  // 评论id
          "content": "这是一条测试回复", // 回复内容
          "created_at": "2025-05-29T15:14:18.096316+08:00",
          "id": 2,  // 回复id
          "updated_at": "2025-05-29T15:14:18.096316+08:00",
          "user_id": "1" // 回复的用户id
        }
      ],
      "replies_count": 1, // 回复数量
      "updated_at": "2025-05-29T15:06:53.544008+08:00",
      "user_id": "1  // 评论的用户id
    }
  ],
  "current_page": 1,
  "page_size": 10,
  "total_count": 1,
  "total_pages": 1
}
```

## 在指定论文下添加评论

```jsx
POST /papers/:id/comcomments

id = (论文id)

示例：
POST /papers/2880a9c9-ff10-52fe-88c0-a18c81550007/comments

//header
Authorization: Bearer <ACCESS_TOKEN>

//request
{
	 "id": 论文id
	 "content" : "这是一条测试评论"
}

//reponse
{
	"comment":{
			"id":1,  //评论id
			"user_id":"1",  //用户id
			"paper_id":"2880a9c9-ff10-52fe-88c0-a18c81550007",
			"paper_title":"A Novel Smart Healthcare Design, Simulation, and Implementation Using Healthcare 4.0 Processes",
			"content":"这是一条测试评论",
			"created_at":"2025-05-29T15:06:53.544008+08:00",
			"updated_at":"2025-05-29T15:06:53.544008+08:00"
	}，
	"message":"comment added successfully"
}
```

## 在指定评论下回复

```jsx
POST /papers/comments/:id/replies

id = 评论id

示例：
POST /papers/comments/1/replies

//header
Authorization: Bearer <ACCESS_TOKEN>

//request
{
	"content": "这是一条测试回复"
}

//reponse
{
    "message": "reply added successfully",
    "reply": {
        "id": 2,    // 评论id
        "comment_id": 1,   // 回复id
        "user_id": "1",   // 用户id
        "content": "这是一条测试回复",
        "created_at": "2025-05-29T15:14:18.096316+08:00",
        "updated_at": "2025-05-29T15:14:18.096316+08:00"
    }
}
```

## 获取用户所有评论（用于个人页）

```jsx
GET /papers/comments/user

//header
Authorization: Bearer <ACCESS_TOKEN>

//reponse
{
    "comments": [
        {
            "content": "这是一条测试评论",
            "created_at": "2025-05-29T15:06:53.544008+08:00",
            "id": 2,
            "paper_id": "2880a9c9-ff10-52fe-88c0-a18c81550007",
            "paper_title": "A Novel Smart Healthcare Design, Simulation, and Implementation Using Healthcare 4.0 Processes",
            "replies_count": 1,
            "updated_at": "2025-05-29T15:06:53.544008+08:00",
            "user_id": "1"
        }
    ],
    "count": 1
}
```

## 删除评论（只能删除自己的）

```jsx
DELETE /papers/comments/:id

id = 评论id

示例：
DELETE /papers/comments/2

//header
Authorization: Bearer <ACCESS_TOKEN>

//reponse
{
	"message": "comment deleted successfully"
}

```

## 删除回复（只能删除自己的）

```jsx
DELETE /papers/replies/:id

id = 回复id

示例：
DELETE /papers/replies/1

//header
Authorization: Bearer <ACCESS_TOKEN>

//reponse
{
	"message": "reply deleted successfully",
}
```

## 获取用户所有的笔记（用于个人页）

```jsx
GET /papers/notes

//header
Authorization: Bearer <ACCESS_TOKEN>

//reponse
{
    "count": 2,
    "notes": [
        {
            "id": 3,  // 笔记id
            "user_id": "1",
            "paper_id": "1eb1aefe-5c8f-5224-8180-61a4ed18d4fe",
            "paper_title": "Subject information integration of higher education institutions in the context of Web3.0",
            "content": "更多笔记",
            "created_at": "2025-05-29T15:55:12.835274+08:00",
            "updated_at": "2025-05-29T15:55:12.835274+08:00"
        },
        {
            "id": 1,  // 笔记id
            "user_id": "1",
            "paper_id": "2880a9c9-ff10-52fe-88c0-a18c81550007",
            "paper_title": "A Novel Smart Healthcare Design, Simulation, and Implementation Using Healthcare 4.0 Processes",
            "content": "再来一条笔记",
            "created_at": "2025-05-29T15:48:36.667735+08:00",
            "updated_at": "2025-05-29T15:54:13.773717+08:00"
        }
    ]
}
```

## 获取用户在指定论文的笔记

```jsx
GET /papers/:id/notes

id = 论文id

示例：
GET /papers/2880a9c9-ff10-52fe-88c0-a18c81550007/notes

//header
Authorization: Bearer <ACCESS_TOKEN>

//reponse
{
    "note": {
        "id": 1, // 笔记id
        "user_id": "1",
        "paper_id": "2880a9c9-ff10-52fe-88c0-a18c81550007",
        "paper_title": "A Novel Smart Healthcare Design, Simulation, and Implementation Using Healthcare 4.0 Processes",
        "content": "这是我的个人笔记内容",
        "created_at": "2025-05-29T15:48:36.667735+08:00",
        "updated_at": "2025-05-29T15:48:36.667735+08:00"
    }
}
```

## 添加/更新 用户在某个论文下的笔记

```jsx
POST /papers/:id/notes

id = 论文id

示例：
POST papers/2880a9c9-ff10-52fe-88c0-a18c81550007/notes

//header
Authorization: Bearer <ACCESS_TOKEN>

//request
{
	"content": "这是我的个人笔记内容"
}

//reponse
{
    "message": "note saved successfully",
    "note": {
        "id": 1, // 笔记id
        "user_id": "1",
        "paper_id": "2880a9c9-ff10-52fe-88c0-a18c81550007",
        "paper_title": "A Novel Smart Healthcare Design, Simulation, and Implementation Using Healthcare 4.0 Processes",
        "content": "这是我的个人笔记内容",
        "created_at": "2025-05-29T15:48:36.667735+08:00",
        "updated_at": "2025-05-29T15:48:36.667735+08:00"
    }
}
```

## 删除笔记 (根据笔记id删除笔记)

```jsx
DELETE /papers/notes/:id

id = 笔记id

示例：
DELETE  /papers/notes/1

//header
Authorization: Bearer <ACCESS_TOKEN>

//reponse
{
	"message":"note deleted successfully"
}
```

## 删除指定论文的笔记

```jsx
DELETE /papers/:id/notes

id = 论文id

示例：
DELETE /papers/2880a9c9-ff10-52fe-88c0-a18c81550007/notes

//header
Authorization: Bearer <ACCESS_TOKEN>

//reponse
{
	"message":"note deleted successfully"
}
```

## 获取用户排行榜

```jsx
GET /users/leaderboard

//header
Authorization: Bearer <ACCESS_TOKEN>
//如果不带jwt，则is_followed都是false，如果带jwt会根据用户情况显示

//reponse
{
  "leaderboard": [
    {
      "rank": 1,
      "id": 2,
      "name": "mDdPude1Ue3",
      "image": "/avatar-smile.svg",
      "points": 0,
      "is_followed": false
    },
    {
      "rank": 2,
      "id": 1,
      "name": "Yn3R2",
      "image": "/avatar-smile.svg",
      "points": 0,
      "is_followed": false
    }
  ]
}
```

## 关注用户

```jsx
POST /users/:id/follow 

id = 用户id

//header
Authorization: Bearer <ACCESS_TOKEN>

示例：
POST /users/59/follow 

//header
Authorization: Bearer <ACCESS_TOKEN>

//reponse
{
	"message":"User followed successfully",
	"success":true
}

```

## 取消关注用户

```jsx
DELETE /users/:id/follow

id = 用户id

//header
Authorization: Bearer <ACCESS_TOKEN>

示例：
DELETE /users/59/follow

//reponse
{
	"message":"User unfollowed successfully",
	"success":true
}
```

## 获取用户个人信息

```jsx
GET /users/profile

//header
Authorization: Bearer <ACCESS_TOKEN>

//reponse
{
    "profile": {
        "id": 1,
        "name": "Yn3R2",
        "user_name": "oJ6KRWx34",
        "image": "/avatar-smile.svg",
        "address": "0x1234567890abcdef",
        "points": 0,
        "followers_count": 0,
        "following_count": 0,
        "is_followed": false,
        "created_at": "2025-05-27T18:07:12.524205+08:00"
    }
}
```

# 协作文档类

用户角色role有三种类型：

owner ： 创建者有所有权限

editor：   编辑者有读、写权限

viewer：  观察者有读权限

## 用户获取文档列表

```jsx
GET /documents

//header
Authorization: Bearer <ACCESS_TOKEN>

//reponse
{
    "count": 6,
    "documents": [
        {
            "collab_count": 1,  // 协作者数量
            "collaborators": [ // 协作者信息
                {
                    "document_id": "da8280d3-c5d8-4d81-815f-14b786246fc4",
                    "user_id": "1",
                    "role": "owner",  // owner or editor or viewer
                    "joined_at": "2025-06-04T10:15:26.071238+08:00"
                }
            ],
            "document": {
                "id": "da8280d3-c5d8-4d81-815f-14b786246fc4", // 文档id
                "title": "update 测试", // 文档标题
                "content": "", // 内容
                "owner_id": "1", // 创建者
                "is_public": false,  // 是否公开
                "version": 2, // 文档版本
                "created_at": "2025-06-04T10:15:26.071238+08:00",
                "updated_at": "2025-06-04T10:21:19.127642+08:00",
                "last_edit_by": "1"  // 最后一次编辑人
            }
        },
    ]
}
```

## 创建文档

```jsx
POST /documents

//header
Authorization: Bearer <ACCESS_TOKEN>

// reqeust
{
	"title" : "文档标题",
	"is_public":  true or false // 是否设置文档为公开
}

// reponse
{
    "collaborators": [  // 协作者信息
        {
            "document_id": "6dfa51ff-738b-4f74-8127-2f8f50c18573",
            "user_id": "1",
            "role": "owner",
            "joined_at": "2025-06-04T10:37:20.916672+08:00"
        }
    ],
    "count": 1,
    "document": {
        "id": "6dfa51ff-738b-4f74-8127-2f8f50c18573", // 文档id
        "title": "post 测试标题", // 标题
        "content": "", // 内容
        "owner_id": "1",
        "is_public": true,
        "version": 1,
        "created_at": "2025-06-04T10:37:20.916672+08:00",
        "updated_at": "2025-06-04T10:37:20.916672+08:00",
        "last_edit_by": "1"
    },
    "message": "document created successfully"
}
```

## 更新文档

```jsx
POST /documents/:id

id = 论文id

//header
Authorization: Bearer <ACCESS_TOKEN>

// request
{
	"title": "标题",
	"content": “内容”,
	"is_public": true or false
}

//reponse
{
    "collaborators": [
        {
            "document_id": "da8280d3-c5d8-4d81-815f-14b786246fc4",
            "user_id": "1",
            "role": "owner",
            "joined_at": "2025-06-04T10:15:26.071238+08:00"
        }
    ],
    "count": 1,
    "document": {
        "id": "da8280d3-c5d8-4d81-815f-14b786246fc4",
        "title": "update 测试213",
        "content": "测试了",
        "owner_id": "1",
        "is_public": false,
        "version": 3,
        "created_at": "2025-06-04T10:15:26.071238+08:00",
        "updated_at": "2025-06-04T10:38:23.06866+08:00",
        "last_edit_by": "1",
        "collaborators": [
            "1"
        ]
    },
    "message": "document updated successfully"
}
```

## 删除文档 (只有owner权限才能删除)

```jsx
DELETE /documents/:id

id = 论文id

//header
Authorization: Bearer <ACCESS_TOKEN>

//reponse 200
{
    "message": "document deleted successfully"
}

// reponst 500
{
    "details": "failed to get document: failed to get document: no rows in result set",
    "message": "document deletion failed"
}
```

## 根据文档id获取协作者

```jsx
GET /documents/:id/collaborators

id = 文档id

示例：
GET /documents/e6bdbf15-9a73-4891-b7af-b2c1d7c3b3a9/collaborators

//header
Authorization: Bearer <ACCESS_TOKEN>

// reponse
{
    "collaborators": [
        {
            "document_id": "e6bdbf15-9a73-4891-b7af-b2c1d7c3b3a9",
            "user_id": "1",
            "role": "owner",
            "joined_at": "2025-06-03T16:57:22.351649+08:00"
        },
        {
            "document_id": "e6bdbf15-9a73-4891-b7af-b2c1d7c3b3a9",
            "user_id": "2",
            "role": "editor",
            "joined_at": "2025-06-04T10:50:08.299125+08:00"
        }
    ],
    "count": 2
}
```

## 添加协作者

```jsx
POST /documents/:id/collaborators

id = 文档id

示例：
POST /documents/e6bdbf15-9a73-4891-b7af-b2c1d7c3b3a9/collaborators

//header
Authorization: Bearer <ACCESS_TOKEN>

//request
{
	"user_id": "2",
	"role": "editor"  //. editor or viewer
}

//reponse 200 
{
	"message": "add collaborator successfully"
}

```

## 移除协作者

```jsx
DELETE /documents/:id/collaborators/:user_id

id = 文档id
user_id = 用户id

示例：
DELETE /documents/e6bdbf15-9a73-4891-b7af-b2c1d7c3b3a9/collaborators/2

//reponse
{
	"message": "remove collaborator successfully"
}
```

## 在线编辑文档内容

只有拥有editor或owner角色的用户才能发送操作消息

所有用户（包括viewer角色）都可以接收操作广播和查看文档状态

客户端应该定期发送ping消息以保持连接活跃

服务器会每10秒发送一次ping消息
如果60秒内没有收到响应，连接将被关闭

### websocket连接

```jsx
/neo4j/v1/documents/:id/ws?token=

id = 文档id
token = 用户jwt

示例：
wss://test.nftkash.xyz/neo4j/v1/documents/e6bdbf/ws?token=ey.....
ws://test.nftkash.xyz/neo4j/v1/documents/e6bdbf/ws?token=ey.....

const fullUrl=wss://test.nftkash.xyz/neo4j/v1/documents/e6bdbf/ws?token=ey.....
socket = new WebSocket(fullUrl);
```

### websocket消息格式

```jsx
{
  "type": "消息类型",
  "payload": {
    // 消息内容，根据消息类型不同
  }
}
```

### 客户端发送的消息类型

1. **操作消息(operation)**

```jsx
{
  "type": "operation",
  "payload": {
    "type": "insert|delete|replace", // 操作类型
    "position": 123, // 操作位置（从0开始的索引）
    "content": "要插入或替换的内容" // 对于delete操作，这是要删除的内容
  }
}
```

2.**光标更新(cursor_update)**

```jsx
{
  "type": "cursor_update",
  "payload": {
    "position": 123 // 光标位置
  }
}
```

3.**请求文档状态 (request_document_state)（当客户端需要获取最新文档状态）**

```json
{
  "type": "request_document_state",
  "payload": {}
}
```

4.**保存文档(save)**

```json
{
  "type": "save",
  "payload": {
    "title": "文档标题",
    "content": "文档完整内容",
    "is_public": true // 是否公开文档
  }
}
```

5.**心跳消息，发送ping消息保持活跃连接 （可发可不发）(ping)**

```json
{
  "type": "ping",
  "payload": {
    "time": 1749008240 // 当前时间戳
  }
}
```

### 服务器后端发送的消息类型

1.**认证响应 (auth_response)（ws连接后对用户认证的响应）**

```json
{
  "type": "auth_response",
  "payload": {
    "success": true,
    "message": "authentication successful"
  }
}
```

2.**文档状态 (document_state) （服务器发送当前文档的完整状态）**

```jsx
{
  "type": "document_state",
  "payload": {
    "document": {
      "id": "doc123",
      "title": "文档标题",
      "content": "文档内容",
      "owner_id": "1",
      "is_public": true,
      "version": 42,
      "created_at": "2025-06-04T110:00:00Z",
      "updated_at": "2025-06-04T110:30:00Z",
      "last_edit_by": "1"
    },
    "can_edit": true, // 用户是否有编辑权限
    "role": "editor" // 用户在文档中的角色
  }
}
```

3.**操作广播 (operation) (服务器广播用户操作给其他用户)**

```jsx
{
  "type": "operation",
  "payload": {
    "id": "op123",
    "document_id": "doc123",
    "user_id": "1",
    "type": "insert",
    "position": 42,
    "content": "新插入的内容",
    "version": 43,
    "timestamp": "2025-06-04T110:00:00Z"
  }
}
```

4.**光标更新广播 (cursor_update) （广播用户的光标位置给其他用户）**

```jsx
{
  "type": "cursor_update",
  "payload": {
    "user_id": "1",
    "session_id": "session789",
    "position": 42
  }
}
```

5.**用户加入通知 (user_joined)**

```jsx
{
  "type": "user_joined",
  "payload": {
    "user_id": "1",
    "session_id": "session123"
  }
}
```

6.**用户离开通知 (user_left)**

```jsx
{
  "type": "user_left",
  "payload": {
    "user_id": "2",
    "session_id": "session123"
  }
}
```

7.**活跃会话列表 (active_sessions) （服务器发送当前文档的所有活跃会话信息）**

```jsx
{
  "type": "active_sessions",
  "payload": {
    "sessions": [
      {
        "id": "session123",
        "document_id": "doc123",
        "user_id": "1",
        "connected": true,
        "cursor_pos": 42,
        "started_at": "2025-06-04T110:30:00Z",
        "last_active": "2025-06-04T110:30:00Z"
      },
      // 更多会话...
    ]
  }
}
```

1. **错误消息 (error) (当操作失败或发生错误时，服务器发送错误消息)**

```jsx
{
  "type": "error",
  "payload": {
    "message": "错误描述信息"
  }
}
```

1. **心跳响应 (pong） （服务端对客户端发送的ping消息做回应）**

```jsx
{
  "type": "pong",
  "payload": {
    "time": 1749008240
  }
}
```

1. **心跳检测（ping） （定时发送ping以避免断开连接）**

```jsx
{
  "type": "ping",
  "payload": {
    "time": 1749008240
  }
}
```