﻿
Процедура ПередЗаписью(Отказ)
	
	Если ПН Тогда
		Если НЕ ЗначениеЗаполнено(ПНВремя) или НЕ ЗначениеЗаполнено(ПНВремя2) Тогда
			Сообщить("Не заполнено время у Понедельника!");
			Отказ = Истина;
		КонецЕсли;
		Если ЗначениеЗаполнено(ПНВремя) и ПНВремя>ПНВремя2 Тогда
			Сообщить("Не верное время у Понедельника!");
			Отказ = Истина;
		КонецЕсли;
		
	КонецЕсли;
	
	Если ВТ Тогда
		Если НЕ ЗначениеЗаполнено(ВТВремя) или НЕ ЗначениеЗаполнено(ВТВремя2) Тогда
			Сообщить("Не заполнено время у Вторника!");
			Отказ = Истина;
		КонецЕсли;
		Если ЗначениеЗаполнено(ВТВремя) и ВТВремя>ВТВремя2 Тогда
			Сообщить("Не верное время у Вторника!");
			Отказ = Истина;
		КонецЕсли;
		
	КонецЕсли;
	
	Если СР Тогда
		Если НЕ ЗначениеЗаполнено(СРВремя) или НЕ ЗначениеЗаполнено(СРВремя2) Тогда
			Сообщить("Не заполнено время у Среды!");
			Отказ = Истина;
		КонецЕсли;
		Если ЗначениеЗаполнено(СРВремя) и СРВремя>СРВремя2 Тогда
			Сообщить("Не верное время у Среды!");
			Отказ = Истина;
		КонецЕсли;
		
	КонецЕсли;
	
	Если ЧТ Тогда
		Если НЕ ЗначениеЗаполнено(ЧТВремя) или НЕ ЗначениеЗаполнено(ЧТВремя2) Тогда
			Сообщить("Не заполнено время у Четверга!");
			Отказ = Истина;
		КонецЕсли;
		Если ЗначениеЗаполнено(ЧТВремя) и ЧТВремя>ЧТВремя2 Тогда
			Сообщить("Не верное время у Четверга!");
			Отказ = Истина;
		КонецЕсли;
		
	КонецЕсли;
	
	Если ПТ Тогда
		Если НЕ ЗначениеЗаполнено(ПТВремя) или НЕ ЗначениеЗаполнено(ПТВремя2) Тогда
			Сообщить("Не заполнено время у Пятницы!");
			Отказ = Истина;
		КонецЕсли;
		Если ЗначениеЗаполнено(ПТВремя) и ПТВремя>ПТВремя2 Тогда
			Сообщить("Не верное время у Пятницы!");
			Отказ = Истина;
		КонецЕсли;
		
	КонецЕсли;
	
	Если СБ Тогда
		Если НЕ ЗначениеЗаполнено(СБВремя) или НЕ ЗначениеЗаполнено(СБВремя2) Тогда
			Сообщить("Не заполнено время у Субботы!");
			Отказ = Истина;
		КонецЕсли;
		Если ЗначениеЗаполнено(СБВремя) и СБВремя>СБВремя2 Тогда
			Сообщить("Не верное время у Субботы!");
			Отказ = Истина;
		КонецЕсли;
		
	КонецЕсли;
	
	Если ВС Тогда
		Если НЕ ЗначениеЗаполнено(ВСВремя) или НЕ ЗначениеЗаполнено(ВСВремя2) Тогда
			Сообщить("Не заполнено время у Воскресения!");
			Отказ = Истина;
		КонецЕсли;
		Если ЗначениеЗаполнено(ВСВремя) и ВСВремя>ВСВремя2 Тогда
			Сообщить("Не верное время у Воскресения!");
			Отказ = Истина;
		КонецЕсли;
		
	КонецЕсли;
	
КонецПроцедуры
