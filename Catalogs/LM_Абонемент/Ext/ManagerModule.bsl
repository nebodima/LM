﻿
Процедура ОбработкаПолученияПредставления(Данные, Представление, СтандартнаяОбработка)
	
	СтандартнаяОбработка = Ложь;
	
	Статус = "";
	Если Данные.Ссылка.Активный Тогда
		Если Данные.Ссылка.Приостановка Тогда
			Статус = " (ПРИОСТАНОВЛЕН)";
		Иначе
			Статус = "";
		КонецЕсли;
	Иначе
		Статус = " (НЕАКТИВНЫЙ)";
	КонецЕсли;
		
	Представление = Данные.Ссылка.Наименование+ Статус; 
	
КонецПроцедуры
