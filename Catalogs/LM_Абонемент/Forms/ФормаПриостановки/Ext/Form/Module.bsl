﻿
&НаКлиенте
Процедура ПриЗакрытии(ЗавершениеРаботы)
	
	С = Новый Структура;
	С.Вставить("СрокПриостановки",СрокПриостановки);
	С.Вставить("Причина",Причина);
	
	ОповеститьОВыборе(С);
	
КонецПроцедуры

&НаКлиенте
Процедура Отмена(Команда)
	СрокПриостановки = 0;
	Причина = "";
	Закрыть();
КонецПроцедуры

&НаКлиенте
Процедура СрокПриостановкиПриИзменении(Элемент)
	
	Если СрокПриостановки <> 0 Тогда
		ДатаВозобновления = НачалоДня(ТекущаяДата()) + (СрокПриостановки * 86400);
	Иначе
		ДатаВозобновления = ТекущаяДата();	
	КонецЕсли; 	

КонецПроцедуры

&НаКлиенте
Процедура ДатаВозобновленияПриИзменении(Элемент)
	
	Если ЗначениеЗаполнено(ДатаВозобновления) Тогда
		СрокПриостановки = -(НачалоДня(ТекущаяДата()) - НачалоДня(ДатаВозобновления)) / 86400;
	Иначе
		СрокПриостановки = 0;	
	КонецЕсли; 	
	
КонецПроцедуры

&НаКлиенте
Процедура ПриОткрытии(Отказ)
	ДатаВозобновления = ТекущаяДата();
КонецПроцедуры
