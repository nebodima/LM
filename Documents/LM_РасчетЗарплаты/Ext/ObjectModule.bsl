﻿
Процедура ПередЗаписью(Отказ, РежимЗаписи, РежимПроведения)
	
	Если НЕ ЗначениеЗаполнено(АвторДокумента) Тогда
		АвторДокумента = ПользователиКлиентСервер.ТекущийПользователь();
	КонецЕсли; 

КонецПроцедуры

Процедура ПриКопировании(ОбъектКопирования)
	
	АвторДокумента = Неопределено;
	Комментарий    = Неопределено;
	
	Если Не ЗначениеЗаполнено(ОбъектКопирования.Организация) Тогда
		LMНастроки = РегистрыСведений.LM_Настройки.ПолучитьПоследнее(ТекущаяДата());
		ЗаполнитьЗначенияСвойств(ЭтотОбъект, LMНастроки);
	КонецЕсли;

КонецПроцедуры

Процедура ОбработкаЗаполнения(ДанныеЗаполнения, ТекстЗаполнения, СтандартнаяОбработка)
	
	Если ЭтоНовый() Тогда
		LMНастроки = РегистрыСведений.LM_Настройки.ПолучитьПоследнее(ТекущаяДата());
		ЗаполнитьЗначенияСвойств(ЭтотОбъект, LMНастроки);
	КонецЕсли;

КонецПроцедуры
