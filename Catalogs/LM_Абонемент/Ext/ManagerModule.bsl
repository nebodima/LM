﻿
Процедура ОбработкаПолученияПредставления(Данные, Представление, СтандартнаяОбработка)
	
	СтандартнаяОбработка = Ложь;
	
	Статус = "";
	
	ТекДата = ТекущаяДата();
	
	Если Данные.Ссылка.Активный Тогда
		
		Для Каждого СтрПриостановка из Данные.Ссылка.Приостановки Цикл 			
			Если ТекДата > СтрПриостановка.ДатаПриостановки и ТекДата < СтрПриостановка.ДатаВозобновления Тогда
				Статус = " (приостановлен до " +Формат(СтрПриостановка.ДатаВозобновления,"ДФ=dd.MM.yy")+ ")";
				Прервать;
			КонецЕсли;			
		КонецЦикла;
		
	Иначе
		Статус = " (НЕАКТИВНЫЙ)";
	КонецЕсли;
	
	Представление = Данные.Ссылка.Наименование+ Статус; 
	
КонецПроцедуры
