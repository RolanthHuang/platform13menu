/* Platform 13 menu data.
 * Edit this file to change items, prices or pictures.
 *
 * price: a number, or { hot: 130, ice: 140 } for drinks, or a string such as '以現場報價為準'.
 * imgs:  list of pictures shown for the item, first one is the cover.
 *        { src: 'photos/xxx', kind: 'photo' | 'illust', cap: '說明' }
 *        'photos/xxx' means assets/img/photos/xxx.webp (+ xxx-sm.webp thumbnail).
 *        Leave imgs empty to show "照片準備中".
 * tags:  'decaf' (無咖啡因), 'season' (季節限定), 'pot' (熱飲一壺)
 */
window.P13 = {
  shop: {
    name: 'Platform 13',
    quote: ['喝杯咖啡', '吃點東西', '不要急', '活著很好'],
    quoteBy: '小貓咪的智慧要聽',
    rules: [
      '全店皆為蔬食，無提供肉類製品',
      '內用低消每人一份餐點（不含點心類）或一杯飲品',
      '禁用外食，慶生蛋糕不受此限',
      '開放插座是想讓大家辦公便利，能源需要一起珍惜（例如：電源不提供打包外帶的服務～）',
      '若很喜歡我們的環境且有長時間用電需求，歡迎適時追加餐點飲品，支持我們長久經營',
      '小店空間座位有限，如遇客滿候位，一起讓其他餓著肚子的客人有用餐的機會',
      '其餘時間無用餐時間限制，請輕鬆享受月台的日常',
      '不收服務費，但別忘了相互尊重唷'
    ]
  },

  categories: [
    {
      id: 'light', zh: '輕蔬食', en: 'Light Meal',
      note: '搭配單點飲品，飲品享 8 折', noteEn: '20% off drinks ordered with it',
      cover: 'photos/wrap-orange-tea',
      items: [
        { id: 'banana-toast', zh: '煎香蕉煙燻培根與麵包', en: 'Veggie Smoked Bacon and Pan-fried Banana on Toast', price: 200,
          imgs: [{ src: 'photos/banana-bacon-toast', kind: 'photo' }] },
        { id: 'blt', zh: 'BLT 早安三明治', en: 'Veggie Smoked Bacon, Lettuce, Tomato Sandwich', price: 180,
          extra: '夾蛋 +20', imgs: [] },
        { id: 'focaccia', zh: '野菇佛卡夏／烤時蔬佛卡夏', en: 'Stir-fried Mushroom or Grilled Vegetables with Focaccia', price: 220,
          imgs: [{ src: 'photos/focaccia', kind: 'photo', cap: '佛卡夏，附薯條與沙拉' }] },
        { id: 'wrap', zh: '野菇捲餅／烤時蔬捲餅', en: 'Stir-fried Mushroom Roll or Grilled Vegetables Roll', price: 220,
          imgs: [
            { src: 'photos/wrap-orange-tea', kind: 'photo', cap: '烤時蔬捲餅，搭配橙香冰茶' },
            { src: 'photos/wrap-eggs', kind: 'photo', cap: '烤時蔬捲餅，加點太陽蛋' },
            { src: 'photos/wrap-salad', kind: 'photo', cap: '烤時蔬捲餅，附薯條與沙拉' }
          ] },
        { id: 'garden-salad', zh: '田園沙拉', en: 'Seasonal Salad', price: 180,
          imgs: [{ src: 'photos/garden-salad', kind: 'photo', cap: '照片是拼盤附的田園沙拉，單點份量以現場為準' }] },
        { id: 'caesar', zh: '凱撒沙拉', en: 'Caesar Salad', price: 180, imgs: [] },
        { id: 'caesar-patty', zh: '嫩排凱撒沙拉', en: 'Caesar Salad with Fried Veggie Patty', price: 250, imgs: [] }
      ],
      addons: {
        zh: '拼盤加點', en: 'Something on the side',
        items: [
          { zh: '蛋（炒蛋／太陽蛋）', en: 'Eggs your way: scrambled or sunny side up', price: '+40', img: 'photos/eggs' },
          { zh: '香料菇菇', en: 'Mushroom', price: '+40' },
          { zh: '薯條', en: 'Chips', price: '+40', img: 'photos/chips' },
          { zh: '煙燻培根', en: 'Veggie smoked bacon', price: '+40' }
        ]
      }
    },

    {
      id: 'main', zh: '主食', en: 'Main Dish',
      note: '搭配單點飲品，飲品享 8 折', noteEn: '20% off drinks ordered with it',
      items: [
        { id: 'hotdog', zh: '起司熱狗堡', en: 'Veggie Hot Dog with Cheese', price: 200,
          imgs: [{ src: 'photos/hotdog', kind: 'photo', cap: '附洋芋片、馬鈴薯沙拉與水果' }] },
        { id: 'burger', zh: '香酥嫩排堡', en: 'Fried Veggie Patty Burger', price: 220, imgs: [] },
        { id: 'lasagne-veg', zh: '蕃茄時蔬千層麵', en: 'Lasagne with Seasonal Vegetables', price: 250,
          imgs: [{ src: 'photos/lasagne-veg', kind: 'photo', cap: '搭配薯條、洋芋片與水果' }] },
        { id: 'lasagne-mush', zh: '蘑菇千層麵', en: 'Lasagne with Mushrooms', price: 250, imgs: [] }
      ],
      addons: {
        zh: '升級套餐', en: 'Make it a meal', price: '+140',
        lines: ['薯條或生菜沙拉', '甜點', '紅茶或黑咖啡'],
        linesEn: 'Chips or salad, dessert, black tea or long black',
        foot: '想換其他飲品，可折抵 60 元'
      }
    },

    {
      id: 'tortilla', zh: '脆餅', en: 'Tortilla',
      note: '搭配單點飲品，飲品享 8 折', noteEn: '20% off drinks ordered with it',
      cover: 'photos/apple-tortilla',
      items: [
        { id: 'margherita', zh: '瑪格麗特', en: 'Margherita', price: 199,
          imgs: [{ src: 'photos/margherita', kind: 'photo' }] },
        { id: 'truffle', zh: '松露野菇', en: 'Fungi with White Truffle Oil', price: 199,
          imgs: [{ src: 'photos/truffle', kind: 'photo' }] },
        { id: 'apple', zh: '蘋果鹹焦糖', en: 'Salted Caramel Apple Cinnamon', price: 199,
          imgs: [{ src: 'photos/apple-tortilla', kind: 'photo' }, { src: 'photos/apple-tortilla-2', kind: 'photo' }] }
      ]
    },

    {
      id: 'waffle', zh: '格子鬆餅', en: 'Waffle',
      note: '搭配單點飲品，飲品享 8 折', noteEn: '20% off drinks ordered with it',
      cover: 'photos/strawberry-waffle',
      items: [
        { id: 'plain-waffle', zh: '原味鬆餅（蜂蜜或巧克力）', en: 'Waffle with Honey or Chocolate Sauce', price: 130,
          imgs: [{ src: 'photos/honey-waffle', kind: 'photo', cap: '蜂蜜口味' }] },
        { id: 'banana-waffle', zh: '香蕉巧克力鬆餅', en: 'Waffle with Fresh Banana and Chocolate Sauce', price: 155, imgs: [] },
        { id: 'fruit-waffle', zh: '季節水果鬆餅', en: 'Waffle with Seasonal Fruits, Honey and Chocolate Sauce', price: 185,
          imgs: [
            { src: 'photos/fruit-waffle', kind: 'photo', cap: '水果依季節更換' },
            { src: 'photos/blue-sparkling-waffle', kind: 'photo', cap: '季節水果鬆餅，搭配藍柑橘氣泡飲' }
          ] },
        { id: 'potato-waffle', zh: '馬鈴薯沙拉鬆餅', en: 'Waffle with Smashed Potato Salad and Lettuce', price: 215,
          imgs: [
            { src: 'photos/potato-waffle', kind: 'photo' },
            { src: 'photos/potato-waffle-soup', kind: 'photo', cap: '搭配今日湯與氣泡飲' }
          ] },
        { id: 'strawberry-waffle', zh: '鮮草莓蜂蜜鬆餅', en: 'Fresh Strawberry Honey Waffle', price: '以現場報價為準',
          tags: ['season'], imgs: [{ src: 'photos/strawberry-waffle', kind: 'photo', cap: '季節隱藏版，草莓季才有' }] }
      ],
      addons: {
        zh: '加冰淇淋', en: 'Extra ice cream on the side', price: '+25／球'
      }
    },

    {
      id: 'dessert', zh: '點心', en: 'Side Dish & Dessert',
      cover: 'photos/banana-bread',
      items: [
        { id: 'croissant', zh: '香烤可頌', en: 'Croissant', price: 69, imgs: [] },
        { id: 'croissant-fruit', zh: '鮮奶油水果可頌', en: 'Croissant with Seasonal Fruits', price: 99,
          imgs: [{ src: 'photos/croissant-fruit', kind: 'photo', cap: '水果依季節更換' }] },
        { id: 'croissant-tomato', zh: '蕃茄起司可頌', en: 'Croissant with Tomato and Cheese', price: 99,
          imgs: [{ src: 'photos/croissant-tomato', kind: 'photo' }] },
        { id: 'soup', zh: '今日湯', en: 'Soup of the Day', price: 80,
          imgs: [{ src: 'photos/soup', kind: 'photo', cap: '每日口味不同' }] },
        { id: 'chips', zh: '黃金薯條', en: 'Chips', price: 100, imgs: [{ src: 'photos/chips', kind: 'photo' }] },
        { id: 'nuggets', zh: '雞塊', en: 'Veggie Nuggets', price: 100,
          imgs: [{ src: 'photos/nuggets', kind: 'photo' }, { src: 'photos/nuggets-chamomile', kind: 'photo', cap: '雞塊，搭配西洋甘菊花茶' }] },
        { id: 'brulee', zh: '法式香烤布蕾', en: 'Crème Brûlée', price: 60,
          imgs: [{ src: 'photos/brulee', kind: 'photo' }] },
        { id: 'scone', zh: '手工司康', en: 'Scone', price: 50,
          imgs: [{ src: 'photos/scone-orange-black', kind: 'photo', cap: '手工司康，搭配橙香微光咖啡' }] },
        { id: 'banana-bread', zh: '手工香蕉鬆糕', en: 'Banana Bread', price: 50,
          imgs: [{ src: 'photos/banana-bread', kind: 'photo' }] }
      ]
    },

    {
      id: 'cone', zh: '甜筒', en: 'Coffee Cone',
      cover: 'photos/baileys-cone',
      items: [
        { id: 'coffee-cone', zh: '招牌甜筒咖啡', en: 'Signature Coffee Cone', price: 150,
          imgs: [{ src: 'illust/coffee-cone', kind: 'illust' }] },
        { id: 'baileys-cone', zh: '貝禮詩甜筒可可', en: 'Baileys Chocolate Cone', price: 150,
          imgs: [{ src: 'photos/baileys-cone', kind: 'photo' }, { src: 'photos/baileys-cone-2', kind: 'photo' }] }
      ]
    },

    {
      id: 'coffee', zh: '咖啡', en: 'Coffee',
      cover: 'photos/mocha',
      items: [
        { id: 'espresso', zh: '濃縮咖啡', en: 'Espresso', price: { hot: 90 }, imgs: [{ src: 'illust/espresso', kind: 'illust' }] },
        { id: 'long-black', zh: '美式咖啡', en: 'Long Black', price: { hot: 100, ice: 110 }, flavour: true,
          imgs: [{ src: 'illust/long-black', kind: 'illust' }] },
        { id: 'latte', zh: '拿鐵', en: 'Latte', price: { hot: 130, ice: 140 }, flavour: true,
          imgs: [{ src: 'illust/latte', kind: 'illust' }] },
        { id: 'cappuccino', zh: '卡布奇諾', en: 'Cappuccino', price: { hot: 130 }, imgs: [{ src: 'illust/cappuccino', kind: 'illust' }] },
        { id: 'flat-white', zh: '小白咖啡', en: 'Flat White', price: { hot: 130 }, imgs: [{ src: 'illust/flat-white', kind: 'illust' }] },
        { id: 'affogato', zh: '阿法奇朵', en: 'Affogato', price: 130, imgs: [{ src: 'illust/affogato', kind: 'illust' }] },
        { id: 'mocha', zh: '摩卡', en: 'Mocha', price: { hot: 140, ice: 160 }, imgs: [{ src: 'photos/mocha', kind: 'photo' }] },
        { id: 'cranberry-black', zh: '蔓越莓微光咖啡', en: 'Cranberry Long Black', price: { ice: 140 },
          imgs: [{ src: 'photos/cranberry-black', kind: 'photo', cap: '蔓越莓冰茶與濃縮分開上，自己倒進去' }] },
        { id: 'orange-black', zh: '橙香微光咖啡', en: 'Orange Long Black', price: { ice: 140 },
          imgs: [{ src: 'photos/scone-orange-black', kind: 'photo', cap: '橙香微光咖啡，搭配手工司康' }] }
      ],
      addons: {
        zh: '加點', en: 'Extras',
        list: [
          { zh: '加風味：焦糖、香草或榛果（美式、拿鐵）', en: 'Caramel, vanilla or hazelnut syrup', price: '+20' },
          { zh: '加一份濃縮', en: 'Extra shot', price: '+30' }
        ]
      }
    },

    {
      id: 'tea', zh: '茶與其他飲品', en: 'Tea & Others',
      cover: 'photos/chamomile-set',
      items: [
        { id: 'chai', zh: '印度茶拿鐵', en: 'Chai Latte', price: { hot: 140, ice: 150 }, imgs: [{ src: 'illust/chai-latte', kind: 'illust' }] },
        { id: 'matcha', zh: '抹茶拿鐵', en: 'Matcha Latte', price: { hot: 140, ice: 150 }, imgs: [{ src: 'illust/matcha-latte', kind: 'illust' }] },
        { id: 'choco', zh: '濃醇巧克力', en: 'Choco Latte', price: { hot: 140, ice: 150 }, imgs: [{ src: 'illust/choco-latte', kind: 'illust' }] },
        { id: 'tea-latte', zh: '英式鮮奶茶', en: 'Black Tea Latte', price: { hot: 130, ice: 140 }, flavour: true,
          imgs: [{ src: 'illust/black-tea-latte', kind: 'illust' }] },
        { id: 'brown-sugar', zh: '黑糖牛奶', en: 'Brown Sugar Latte', price: { hot: 130, ice: 140 }, tags: ['decaf'],
          imgs: [{ src: 'illust/brown-sugar-latte', kind: 'illust' }] },
        { id: 'english', zh: '英式早餐紅茶', en: 'English Breakfast Tea', price: { hot: 100, ice: 110 },
          imgs: [{ src: 'photos/english-tea-hot', kind: 'photo', cap: '熱' }, { src: 'photos/english-tea-iced', kind: 'photo', cap: '冰' }] },
        { id: 'earl-grey', zh: '皇家伯爵茶', en: 'Earl Grey Tea', price: { hot: 100, ice: 110 }, imgs: [{ src: 'illust/earl-grey', kind: 'illust' }] },
        { id: 'chamomile', zh: '西洋甘菊花茶', en: 'Chamomile Herbal Tea', price: { hot: 100, ice: 110 }, tags: ['decaf', 'pot'],
          imgs: [{ src: 'photos/chamomile-set', kind: 'photo', cap: '熱飲一壺' }, { src: 'photos/nuggets-chamomile', kind: 'photo', cap: '和雞塊一起' }] },
        { id: 'peppermint', zh: '薄荷花草茶', en: 'Peppermint Herbal Tea', price: { hot: 100, ice: 110 }, tags: ['decaf', 'pot'],
          imgs: [{ src: 'illust/peppermint-tea', kind: 'illust' }] },
        { id: 'cranberry-tea', zh: '蔓越莓冰茶', en: 'Cranberry Iced Tea', price: { ice: 110 }, tags: ['decaf'],
          imgs: [{ src: 'photos/cranberry-iced-tea', kind: 'photo' }] },
        { id: 'orange-tea', zh: '橙香冰茶', en: 'Orange Iced Tea', price: { ice: 110 }, tags: ['decaf'],
          imgs: [{ src: 'photos/orange-iced-tea', kind: 'photo' }, { src: 'photos/wrap-orange-tea', kind: 'photo', cap: '搭配烤時蔬捲餅' }] }
      ],
      addons: {
        zh: '加點', en: 'Extras',
        list: [{ zh: '英式鮮奶茶加風味：焦糖、香草或榛果', en: 'Syrup for the black tea latte', price: '+20' }]
      }
    },

    {
      id: 'sparkling', zh: '氣泡飲', en: 'Sparkling',
      cover: 'photos/blue-sparkling-2',
      items: [
        { id: 'llb', zh: '檸檬萊姆彼得斯', en: 'Lemon Lime Bitters', price: 130, tags: ['decaf'],
          imgs: [{ src: 'illust/lemon-lime-bitters', kind: 'illust' }] },
        { id: 'raspberry', zh: '覆盆子檸檬氣泡飲', en: 'Raspberry Sparkling', price: 130, tags: ['decaf'],
          imgs: [{ src: 'illust/raspberry-sparkling', kind: 'illust' }] },
        { id: 'peach', zh: '蜜桃檸檬氣泡飲', en: 'Peach Sparkling', price: 130, tags: ['decaf'],
          imgs: [{ src: 'illust/peach-sparkling', kind: 'illust' }] },
        { id: 'blue', zh: '藍柑橘氣泡飲', en: 'Blue Curaçao Sparkling', price: 130, tags: ['decaf'],
          imgs: [{ src: 'photos/blue-sparkling-2', kind: 'photo' }, { src: 'photos/blue-sparkling-3', kind: 'photo', cap: '水果裝飾依季節更換' }, { src: 'photos/blue-sparkling', kind: 'photo' }, { src: 'photos/blue-sparkling-waffle', kind: 'photo', cap: '搭配季節水果鬆餅' }] }
      ]
    }
  ],

  cats: {
    id: 'cats', zh: '店貓', en: 'Shop Cats',
    cover: 'photos/cat-duo',
    list: [
      { id: 'kiki', name: 'KIKI', collar: '橘色頸圈', color: '#d9822b', img: 'photos/cat-kiki',
        line: '地板是我的，你們只是借坐一下。' },
      { id: 'milu', name: '咪嚕', collar: '綠色頸圈', color: '#5fa58a', img: 'photos/cat-milu', more: 'photos/cat-milu-floor',
        line: '這張桌子我先坐了，點完餐再叫我。' },
      { id: 'miancha', name: '麵茶', collar: '虎斑', color: '#9a7a52', img: 'photos/cat-miancha',
        line: '窗邊那個位子，風景比較好。' }
    ],
    duo: 'photos/cat-duo'
  }
};
