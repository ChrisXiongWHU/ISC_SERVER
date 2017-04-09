/**
* jquery.timer.js
* 在网页上显示日期和时间控件
* 使用方法:$('#timeDisp').timer();
* @author SuperBoy
* 日期格式说明:
> 
> *yy: 四位年份,如:2009
> *y : 两位年份,如:09
> *mm: 两位月份,不足在前补0,如:02
> *m : 一位月份,不补0,如:02
> *dd: 月份中的日,两位表示,不足补0,如:02
> *d : 月份中的日,不足补0,如:2
> *W : 星期的全称,如:星期一
> *w : 星期的略称,如:周一
> *HH:24小时制小时,不足两位补0,如:08,13
> *H:24小时制,不补0,如:8,13
> *hh: 12小时制,不足两位补0并且会在加上am或pm进行区分,如01:12:20 am
> *h : 12小时制,不补0并且会在加上am或pm进行区分,如1:12:20 am
> *MM:分钟表示,不足两位补0,如:08
> *M:分钟表示,不补0,如:8
> *ss:秒表示,不足两位补0,如:08
> *s:秒表示,不补0,如:8
> *SSS:表示毫秒
> 
*/
(function($) {
function Timer(){
this._defaults = {
     format: "yy-mm-dd W hh:MM:ss",
     morning : "上午",
     afterNoon : "下午",
     weekNames: ['星期日','星期一','星期二','星期三','星期四','星期五','星期六'],
   weekNamesShort: ['周日','周一','周二','周三','周四','周五','周六']
};
$.extend(this._defaults);
}
$.extend(Timer.prototype, {
_settings : {},
_init: function(target, options){
   this._settings["target"] = target;
   if(!options){
    options = this._defaults;
   }
   this._settings["format"] = options["format"]?options["format"]:this._defaults["format"];
   this._settings["morning"] = options["morning"]?options["morning"]:this._defaults["morning"];
   this._settings["afterNoon"] = options["afterNoon"]?options["afterNoon"]:this._defaults["afterNoon"];
   this._settings["weekNames"] = options["weekNames"]?options["weekNames"]:this._defaults["weekNames"];
   this._settings["weekNamesShort"] = options["weekNamesShort"]?options["weekNamesShort"]:this._defaults["weekNamesShort"];

   setInterval('$.timer._setValue()',1);
},
/**
*yy: 四位年份,如:2009
*y : 两位年份,如:09
*mm: 两位月份,不足在前补0,如:02
*m : 一位月份,不补0,如:02
*dd: 月份中的日,两位表示,不足补0,如:02
*d : 月份中的日,不足补0,如:2
*W : 星期的全称,如:星期一
*w : 星期的略称,如:周一
*HH:24小时制小时,不足两位补0,如:08,13
*H:24小时制,不补0,如:8,13
*hh: 12小时制,不足两位补0并且会在加上am或pm进行区分,如01:12:20 am
*h : 12小时制,不补0并且会在加上am或pm进行区分,如1:12:20 am
*MM:分钟表示,不足两位补0,如:08
*M:分钟表示,不补0,如:8
*ss:秒表示,不足两位补0,如:08
*s:秒表示,不补0,如:8
*SSS:表示毫秒
*/
_formatDate : function(date){
   var format = this._settings["format"];
   var dateStr = format;
   var showHour = dateStr.indexOf('h') != -1;
   dateStr = dateStr.replace(/yy/, date.getFullYear());
   dateStr = dateStr.replace(/y/, (date.getYear()).toString().substr(2));
   dateStr = dateStr.replace(/mm/, this._appendZero(date.getMonth(), 2));
   dateStr = dateStr.replace(/m/, date.getMonth());
   dateStr = dateStr.replace(/dd/, this._appendZero(date.getDate(), 2));
   dateStr = dateStr.replace(/d/, date.getDate());
   dateStr = dateStr.replace(/W/, this._settings["weekNames"][date.getDay()]);
   dateStr = dateStr.replace(/w/, this._settings["weekNamesShort"][date.getDay()]);
   // 24小时制
   dateStr = dateStr.replace(/HH/, this._appendZero(date.getHours(), 2));
   dateStr = dateStr.replace(/H/, date.getHours());
   // 12小时制
   dateStr = dateStr.replace(/hh/, this._appendZero(date.getHours()>12?(date.getHours()-12):date.getHours(), 2));
   dateStr = dateStr.replace(/h/, date.getHours()>12?(date.getHours()-12):date.getHours());
   dateStr = dateStr.replace(/MM/, this._appendZero(date.getMinutes(), 2));
   dateStr = dateStr.replace(/M/, date.getMinutes());
   dateStr = dateStr.replace(/ss/, this._appendZero(date.getSeconds(), 2));
   dateStr = dateStr.replace(/s/, date.getSeconds());
   dateStr = dateStr.replace(/SSS/, this._appendZero(date.getMilliseconds(), 3));
   dateStr = dateStr.replace(/SS/, this._appendZero(date.getMilliseconds(), 2));
   dateStr = dateStr.replace(/S/, date.getMilliseconds());
   if(showHour) {
    if(date.getHours() - 12 >=0) {
     dateStr = dateStr + this._settings["afterNoon"];
    } else {
     dateStr = dateStr + this._settings["morning"];
    }
   }
   return dateStr;
},
_appendZero : function(value, length){
   if(value) {
    value = (value).toString();
    if (value.length < length){
     for(var i = 0; i< length - value.length; i++){
      value = "0" + value;
     }
    }
   }
   return value;
},
_setValue: function(){
   var date = new Date();
   var target = this._settings["target"];
   date = this._formatDate(date)
    if(target.nodeName == "INPUT"){
       $(target).val(date);
    } else {
       $(target).text(date);
    }
}
});
$.fn.timer = function(options) {
return this.each(function() {
   $.timer._init(this, options);
});
}

$.timer = new Timer();

})(jQuery);