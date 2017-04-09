/**
* jquery.timer.js
* ����ҳ����ʾ���ں�ʱ��ؼ�
* ʹ�÷���:$('#timeDisp').timer();
* @author SuperBoy
* ���ڸ�ʽ˵��:
> 
> *yy: ��λ���,��:2009
> *y : ��λ���,��:09
> *mm: ��λ�·�,������ǰ��0,��:02
> *m : һλ�·�,����0,��:02
> *dd: �·��е���,��λ��ʾ,���㲹0,��:02
> *d : �·��е���,���㲹0,��:2
> *W : ���ڵ�ȫ��,��:����һ
> *w : ���ڵ��Գ�,��:��һ
> *HH:24Сʱ��Сʱ,������λ��0,��:08,13
> *H:24Сʱ��,����0,��:8,13
> *hh: 12Сʱ��,������λ��0���һ��ڼ���am��pm��������,��01:12:20 am
> *h : 12Сʱ��,����0���һ��ڼ���am��pm��������,��1:12:20 am
> *MM:���ӱ�ʾ,������λ��0,��:08
> *M:���ӱ�ʾ,����0,��:8
> *ss:���ʾ,������λ��0,��:08
> *s:���ʾ,����0,��:8
> *SSS:��ʾ����
> 
*/
(function($) {
function Timer(){
this._defaults = {
     format: "yy-mm-dd W hh:MM:ss",
     morning : "����",
     afterNoon : "����",
     weekNames: ['������','����һ','���ڶ�','������','������','������','������'],
   weekNamesShort: ['����','��һ','�ܶ�','����','����','����','����']
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
*yy: ��λ���,��:2009
*y : ��λ���,��:09
*mm: ��λ�·�,������ǰ��0,��:02
*m : һλ�·�,����0,��:02
*dd: �·��е���,��λ��ʾ,���㲹0,��:02
*d : �·��е���,���㲹0,��:2
*W : ���ڵ�ȫ��,��:����һ
*w : ���ڵ��Գ�,��:��һ
*HH:24Сʱ��Сʱ,������λ��0,��:08,13
*H:24Сʱ��,����0,��:8,13
*hh: 12Сʱ��,������λ��0���һ��ڼ���am��pm��������,��01:12:20 am
*h : 12Сʱ��,����0���һ��ڼ���am��pm��������,��1:12:20 am
*MM:���ӱ�ʾ,������λ��0,��:08
*M:���ӱ�ʾ,����0,��:8
*ss:���ʾ,������λ��0,��:08
*s:���ʾ,����0,��:8
*SSS:��ʾ����
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
   // 24Сʱ��
   dateStr = dateStr.replace(/HH/, this._appendZero(date.getHours(), 2));
   dateStr = dateStr.replace(/H/, date.getHours());
   // 12Сʱ��
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