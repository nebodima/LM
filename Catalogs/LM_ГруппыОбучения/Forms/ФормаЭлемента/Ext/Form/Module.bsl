﻿
&НаКлиенте
Процедура ПедагогСоздание(Элемент, СтандартнаяОбработка)
	
	СтандартнаяОбработка = Ложь;
	
	ПараметрыСтроки = Новый Структура;
	
	Назв = СокрЛП(Элемент.ТекстРедактирования);
	
	Если Найти(Назв," ") > 0 Тогда
		Симв1 = Найти(Назв," ");
		ПараметрыСтроки.Вставить("Фамилия",Лев(Назв,Симв1-1));
		Назв = СокрЛП(Сред(Назв,Симв1+1));
	Иначе
		ПараметрыСтроки.Вставить("Фамилия",Назв);
		Назв = "";
	КонецЕсли;
	
	Если (Найти(Назв," ") > 0) и (СтрДлина(Назв) > 0) Тогда
		Симв2 = Найти(Назв," ");
		ПараметрыСтроки.Вставить("Имя",Лев(Назв,Симв2-1));
		Назв = СокрЛП(Сред(Назв,Симв2+1));
	Иначе
		ПараметрыСтроки.Вставить("Имя",Назв);
		Назв = "";
	КонецЕсли;
	
	Если СтрДлина(Назв) > 0 Тогда
		ПараметрыСтроки.Вставить("Отчество",Назв);
	КонецЕсли;
	
	ПараметрыСтроки.Вставить("Группа","Педагоги");
	
	Пар = Новый Структура("Ключ2", ПараметрыСтроки);
	
	ОткрытьФорму("Справочник.LM_ФизЛица.Форма.ФормаЭлемента",Пар,ЭтотОбъект,ЭтаФорма.УникальныйИдентификатор,ВариантОткрытияОкна.ОтдельноеОкно,,,РежимОткрытияОкнаФормы.БлокироватьОкноВладельца);

КонецПроцедуры

&НаКлиенте
Процедура ПНПриИзменении(Элемент)
	
	Если Объект.ПН Тогда
		Элементы.ПНВремя.Доступность = Истина;
		Объект.ПНВремя = ?(ЗначениеЗаполнено(Объект.ПНВремя),Объект.ПНВремя,Объект.Время);
	Иначе
		Элементы.ПНВремя.Доступность = Ложь;
		Объект.ПНВремя = Неопределено;
	КонецЕсли;	
		
КонецПроцедуры

&НаКлиенте
Процедура ВТПриИзменении(Элемент)
	
	Если Объект.ВТ Тогда
		Элементы.ВТВремя.Доступность = Истина;
		Объект.ВТВремя = ?(ЗначениеЗаполнено(Объект.ВТВремя),Объект.ВТВремя,Объект.Время);
	Иначе
		Элементы.ВТВремя.Доступность = Ложь;
		Объект.ВТВремя = Неопределено;
	КонецЕсли;
	
КонецПроцедуры

&НаКлиенте
Процедура СРПриИзменении(Элемент)
	
	Если Объект.СР Тогда
		Элементы.СРВремя.Доступность = Истина;
		Объект.СРВремя = ?(ЗначениеЗаполнено(Объект.СРВремя),Объект.СРВремя,Объект.Время);
	Иначе
		Элементы.СРВремя.Доступность = Ложь;
		Объект.СРВремя = Неопределено;
	КонецЕсли;
	
КонецПроцедуры

&НаКлиенте
Процедура ЧТПриИзменении(Элемент)
	
	Если Объект.ЧТ Тогда
		Элементы.ЧТВремя.Доступность = Истина;
		Объект.ЧТВремя = ?(ЗначениеЗаполнено(Объект.ЧТВремя),Объект.ЧТВремя,Объект.Время);
	Иначе
		Элементы.ЧТВремя.Доступность = Ложь;
		Объект.ЧТВремя = Неопределено;
	КонецЕсли;
	
КонецПроцедуры

&НаКлиенте
Процедура ПТПриИзменении(Элемент)
	
	Если Объект.ПТ Тогда
		Элементы.ПТВремя.Доступность = Истина;
		Объект.ПТВремя = ?(ЗначениеЗаполнено(Объект.ПТВремя),Объект.ПТВремя,Объект.Время);
	Иначе
		Элементы.ПТВремя.Доступность = Ложь;
		Объект.ПТВремя = Неопределено;
	КонецЕсли;
	
КонецПроцедуры

&НаКлиенте
Процедура СБПриИзменении(Элемент)
	
	Если Объект.СБ Тогда
		Элементы.СБВремя.Доступность = Истина;
		Объект.СБВремя = ?(ЗначениеЗаполнено(Объект.СБВремя),Объект.СБВремя,Объект.Время);
	Иначе
		Элементы.СБВремя.Доступность = Ложь;
		Объект.СБВремя = Неопределено;
	КонецЕсли;

КонецПроцедуры

&НаКлиенте
Процедура ВСПриИзменении(Элемент)
	
	Если Объект.ВС Тогда
		Элементы.ВСВремя.Доступность = Истина;
		Объект.ВСВремя = ?(ЗначениеЗаполнено(Объект.ВСВремя),Объект.ВСВремя,Объект.Время);
	Иначе
		Элементы.ВСВремя.Доступность = Ложь;
		Объект.ВСВремя = Неопределено;
	КонецЕсли;
	
КонецПроцедуры

&НаКлиенте
Процедура ОбновитьВидимость()
	
	Если Объект.ПН Тогда
		Элементы.ПНВремя.Доступность = Истина;
		Объект.ПНВремя = ?(ЗначениеЗаполнено(Объект.ПНВремя),Объект.ПНВремя,Объект.Время);
	Иначе
		Элементы.ПНВремя.Доступность = Ложь;
		Объект.ПНВремя = Неопределено;
	КонецЕсли;
	
	Если Объект.ВТ Тогда
		Элементы.ВТВремя.Доступность = Истина;
		Объект.ВТВремя = ?(ЗначениеЗаполнено(Объект.ВТВремя),Объект.ВТВремя,Объект.Время);
	Иначе
		Элементы.ВТВремя.Доступность = Ложь;
		Объект.ВТВремя = Неопределено;
	КонецЕсли;
	
	Если Объект.СР Тогда
		Элементы.СРВремя.Доступность = Истина;
		Объект.СРВремя = ?(ЗначениеЗаполнено(Объект.СРВремя),Объект.СРВремя,Объект.Время);
	Иначе
		Элементы.СРВремя.Доступность = Ложь;
		Объект.СРВремя = Неопределено;
	КонецЕсли;
	
	Если Объект.ЧТ Тогда
		Элементы.ЧТВремя.Доступность = Истина;
		Объект.ЧТВремя = ?(ЗначениеЗаполнено(Объект.ЧТВремя),Объект.ЧТВремя,Объект.Время);
	Иначе
		Элементы.ЧТВремя.Доступность = Ложь;
		Объект.ЧТВремя = Неопределено;
	КонецЕсли;
	
	Если Объект.ПТ Тогда
		Элементы.ПТВремя.Доступность = Истина;
		Объект.ПТВремя = ?(ЗначениеЗаполнено(Объект.ПТВремя),Объект.ПТВремя,Объект.Время);
	Иначе
		Элементы.ПТВремя.Доступность = Ложь;
		Объект.ПТВремя = Неопределено;
	КонецЕсли;
	
	Если Объект.СБ Тогда
		Элементы.СБВремя.Доступность = Истина;
		Объект.СБВремя = ?(ЗначениеЗаполнено(Объект.СБВремя),Объект.СБВремя,Объект.Время);
	Иначе
		Элементы.СБВремя.Доступность = Ложь;
		Объект.СБВремя = Неопределено;
	КонецЕсли;
	
	Если Объект.ВС Тогда
		Элементы.ВСВремя.Доступность = Истина;
		Объект.ВСВремя = ?(ЗначениеЗаполнено(Объект.ВСВремя),Объект.ВСВремя,Объект.Время);
	Иначе
		Элементы.ВСВремя.Доступность = Ложь;
		Объект.ВСВремя = Неопределено;
	КонецЕсли;

КонецПроцедуры      

&НаКлиенте
Процедура ПриОткрытии(Отказ)
	ОбновитьВидимость();
КонецПроцедуры

