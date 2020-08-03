﻿
Процедура ПередЗаписью(Отказ)
	
	Если ОбменДанными.Загрузка Тогда
		Возврат;
	КонецЕсли;
	    	
	Если ЭтоНовый() Тогда
		Возврат;
	КонецЕсли;
	
КонецПроцедуры

Процедура ОбработкаЗаполнения(ДанныеЗаполнения, ТекстЗаполнения, СтандартнаяОбработка)
	
	Если ДанныеЗаполнения <> Неопределено Тогда
		Если ЭтоГруппа И ДанныеЗаполнения.Свойство("Владелец") Тогда
			ЭтотОбъект.Владелец = ДанныеЗаполнения.Владелец;
		Иначе
			ЗаполнитьЗначенияСвойств(ЭтотОбъект, ДанныеЗаполнения);
		КонецЕсли;
	КонецЕсли;
	
	Если Не ЭтоГруппа Тогда
		Если НЕ ЗначениеЗаполнено(Организация) Тогда
			LMНастроки = РегистрыСведений.LM_Настройки.ПолучитьПоследнее(ТекущаяДата());
			Организация = LMНастроки.Организация;
		КонецЕсли; 					
	КонецЕсли;

КонецПроцедуры
