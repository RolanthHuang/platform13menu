(function (root) {
 'use strict';
 const traditional={'蓝':'藍','饼':'餅','鲜':'鮮','卷':'捲','热':'熱','时':'時','柠':'檸','马':'馬','铃':'鈴','汤':'湯','汉':'漢','鸡':'雞','块':'塊','红':'紅','绿':'綠','姜':'薑','酥':'酥'};
 function normalize(value){return String(value||'').normalize('NFKD').replace(/\p{M}/gu,'').toLowerCase().replace(/[蓝饼鲜卷热时柠马铃汤汉鸡块红绿姜]/g,c=>traditional[c]||c).replace(/[\s\p{P}\p{S}]/gu,'');}
 function knownPrices(item){return item.variants.map(v=>v.price).filter(Number.isFinite);}
 function basePrice(item){const p=knownPrices(item);return p.length?Math.min(...p):null;}
 function searchItems(data,state,favorites=new Set()){
  const tokens=String(state.q||'').trim().split(/\s+/).filter(Boolean).map(normalize);
  const results=data.items.filter(item=>{
   if(state.category&&state.category!=='all'&&item.category!==state.category)return false;
   if(state.filter==='photos'&&!item.images.some(k=>data.assets[k].kind==='photo'))return false;
   if(state.filter==='seasonal'&&!item.tags.includes('seasonal'))return false;
   if(state.filter==='caffeine-free'&&!item.tags.includes('caffeine-free'))return false;
   if(state.filter==='favorites'&&!favorites.has(item.id))return false;
   const category=data.categories.find(c=>c.id===item.category);
   const fields=[item.name,item.en,item.description,...item.aliases,category?.name,...item.variants.flatMap(v=>[v.id,v.label]),...item.tags].map(normalize);
   return tokens.every(token=>fields.some(field=>field.includes(token)));
  });
  if(state.sort==='price-asc'||state.sort==='price-desc'){
   const direction=state.sort==='price-asc'?1:-1;
   results.sort((a,b)=>{const x=basePrice(a),y=basePrice(b);if(x===null)return y===null?0:1;if(y===null)return -1;return (x-y)*direction;});
  }
  return results;
 }
 function calculatePrice(item,variantId,options={}){
  const variant=item.variants.find(v=>v.id===variantId)||item.variants[0];
  let extra=0;
  if(item.addons==='light'||item.addons==='blt'){
   if(['sunny','scrambled'].includes(options.egg))extra+=item.addons==='blt'?20:40;
   for(const key of ['mushroom','chips','bacon'])if(options[key])extra+=40;
  }
  if(item.addons==='waffle'&&options.iceCream)extra+=25;
  if(item.addons==='meal'&&options.upgrade)extra+=140;
  if(['coffee-flavor','milk-tea-flavor'].includes(item.addons)&&['caramel','vanilla','hazelnut'].includes(options.flavor))extra+=20;
  if(item.category==='coffee'&&options.extraShot)extra+=30;
  return {base:variant.price,extra,total:Number.isFinite(variant.price)?variant.price+extra:null};
 }
 const api={normalize,knownPrices,basePrice,searchItems,calculatePrice};
 if(typeof module==='object'&&module.exports)module.exports=api;else root.MenuModel=api;
})(typeof globalThis==='object'?globalThis:this);
