﻿
&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)	
	
	ЦеныТарифов.Параметры.УстановитьЗначениеПараметра("Тариф",Объект.Ссылка);
	
	Если Объект.Наименование = "" Тогда
		Объект.Наименование = "Тариф " +Формат(ТекущаяДата(),"ДФ=yyyy-MM-dd");
	КонецЕсли;
	
КонецПроцедуры

&НаКлиенте
Процедура ОбработкаОповещения(ИмяСобытия, Параметр, Источник)
	ЦеныТарифов.Параметры.УстановитьЗначениеПараметра("Тариф",Объект.Ссылка);
	ОбновитьВидимость();
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

&НаКлиенте
Процедура ПриОткрытии(Отказ)
	ОбновитьВидимость();
КонецПроцедуры

Процедура ОбновитьВидимость()
	
	Элементы.Декорация1.Заголовок = "";
	Элементы.Декорация2.Заголовок = "";
	
	Если ЗначениеЗаполнено(Объект.Сумма) Тогда
		
		Если Объект.КоличествоЧасов > 0 Тогда
			Элементы.Декорация1.Заголовок = "" +Формат(Объект.Сумма/Объект.КоличествоЧасов,"ЧДЦ=2")+ " за 1 час ("
			+Формат(Объект.Сумма,"ЧДЦ=2")+ " / " +Объект.КоличествоЧасов+ " ч.)";				
		ИначеЕсли Объект.КоличествоУроков > 0 Тогда
			Элементы.Декорация1.Заголовок = "" +Формат(Объект.Сумма/Объект.КоличествоУроков,"ЧДЦ=2")+ " за 1 урок ("
			+Формат(Объект.Сумма,"ЧДЦ=2")+ " / " +Объект.КоличествоУроков+ " ур.)";
		КонецЕсли;
		
		Возврат;
	КонецЕсли;
	
	
	Если НЕ Объект.Ссылка.Пустая() Тогда
		
		Запрос = Новый Запрос;
		Запрос.Текст = 
		"ВЫБРАТЬ ПЕРВЫЕ 1
		|	LM_ЦеныТарифовСрезПоследних.Период КАК Период,
		|	LM_ЦеныТарифовСрезПоследних.КоличествоЧасов КАК КоличествоЧасов,
		|	LM_ЦеныТарифовСрезПоследних.КоличествоУроков КАК КоличествоУроков,
		|	LM_ЦеныТарифовСрезПоследних.Сумма КАК Сумма
		|ИЗ
		|	РегистрСведений.LM_ЦеныТарифов.СрезПоследних(&ТекДата, ) КАК LM_ЦеныТарифовСрезПоследних
		|ГДЕ
		|	LM_ЦеныТарифовСрезПоследних.Тариф = &Тариф
		|
		|УПОРЯДОЧИТЬ ПО
		|	Период УБЫВ";
		Запрос.УстановитьПараметр("Тариф", Объект.Ссылка);
		Запрос.УстановитьПараметр("ТекДата", ТекущаяДата());
		Цены = Запрос.Выполнить().Выгрузить();
		
		Если Цены.Количество() > 0 Тогда
			Если Цены[0].КоличествоЧасов > 0 Тогда
				Элементы.Декорация1.Заголовок = "" +Формат(Цены[0].Сумма/Цены[0].КоличествоЧасов,"ЧДЦ=2")+ " за 1 час ("
				+Формат(Цены[0].Сумма,"ЧДЦ=2")+ " / " +Цены[0].КоличествоЧасов+ " ч.)";				
			ИначеЕсли Цены[0].КоличествоУроков > 0 Тогда
				Элементы.Декорация1.Заголовок = "" +Формат(Цены[0].Сумма/Цены[0].КоличествоУроков,"ЧДЦ=2")+ " за 1 урок ("
				+Формат(Цены[0].Сумма,"ЧДЦ=2")+ " / " +Цены[0].КоличествоУроков+ " ур.)";
			КонецЕсли;
			Элементы.Декорация2.Заголовок = "Действующая цена на " +Формат(Цены[0].Период,"ДЛФ=D")+ ": ";
		Иначе
			Элементы.Декорация2.Заголовок = "";
			Элементы.Декорация1.Заголовок = "Нет действующих цен! Создайте новую цену!";
		КонецЕсли;
		
	КонецЕсли;
	
КонецПроцедуры

&НаКлиенте
Процедура КоличествоЧасовПриИзменении(Элемент)
	Объект.КоличествоУроков = 0;
	ОбновитьВидимость();
КонецПроцедуры

&НаКлиенте
Процедура КоличествоУроковПриИзменении(Элемент)
	Объект.КоличествоЧасов = 0;
	ОбновитьВидимость();
КонецПроцедуры 

&НаКлиенте
Процедура СуммаПриИзменении(Элемент)
	ОбновитьВидимость();
КонецПроцедуры
