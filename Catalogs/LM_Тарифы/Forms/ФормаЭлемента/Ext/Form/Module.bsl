﻿
&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)	
	ЦеныТарифов.Параметры.УстановитьЗначениеПараметра("Тариф",Объект.Ссылка);
КонецПроцедуры

&НаКлиенте
Процедура ОбработкаОповещения(ИмяСобытия, Параметр, Источник)
	ЦеныТарифов.Параметры.УстановитьЗначениеПараметра("Тариф",Объект.Ссылка);
КонецПроцедуры

&НаКлиенте
Процедура СоздатьЦену(Команда) 	
	
	Если Не ЗначениеЗаполнено(Объект.Ссылка) Тогда
		
		Если Не ЗначениеЗаполнено(Объект.Наименование) Тогда
			Сообщить("Не заполнено наименование тарифа!");
			Возврат;
		КонецЕсли;		
		
		Режим = РежимДиалогаВопрос.ДаНет;
		Ответ = Вопрос("Тариф еще не записан! Записать?", Режим, 0);
		Если Ответ = КодВозвратаДиалога.Нет Тогда
			Возврат;
		Иначе
			Записать();
		КонецЕсли;
	КонецЕсли;
	
	ПараметрыФормы = Новый Структура("Тариф", Объект.Ссылка);
	ОткрытьФорму("РегистрСведений.LM_ЦеныТарифов.Форма.ФормаЗаписиТолькоЧтение",ПараметрыФормы,,,ВариантОткрытияОкна.ОтдельноеОкно);

КонецПроцедуры
