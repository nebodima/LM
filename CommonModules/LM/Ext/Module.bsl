﻿Функция ПолучитьОстаткиЧаcовИСумм(Дата, ФизЛицо) Экспорт
	
	Ст = Новый Структура; 	
	
	Запрос = Новый Запрос;
	Запрос.Текст = 
	"ВЫБРАТЬ
	|	СписанияСуммЗаУроки.ЧасыОстаток,
	|	СписанияСуммЗаУроки.СуммаОстаток
	|ИЗ
	|	РегистрНакопления.LM_СписанияСуммЗаУроки.Остатки(&Дата, ) КАК СписанияСуммЗаУроки
	|ГДЕ
	|	СписанияСуммЗаУроки.Клиент = &Клиент"; 	
	Запрос.УстановитьПараметр("Клиент", ФизЛицо);
	Запрос.УстановитьПараметр("Дата", Дата);	
	РезультатЗапроса = Запрос.Выполнить();	
	Остатки = РезультатЗапроса.Выбрать();
	Пока Остатки.Следующий() Цикл
		Ст.Вставить("КоличествоЧасов", '00010101' + Остатки.ЧасыОстаток);
		Ст.Вставить("Сумма", Остатки.СуммаОстаток);		
	КонецЦикла; 
	
	Возврат Ст;
	
КонецФункции

// Проверияет абонементы на длительность
Процедура ПроверкаАбонементов() Экспорт 

	Запрос = Новый Запрос;
	Запрос.Текст = 
	"ВЫБРАТЬ
	|	LM_Абонемент.Ссылка КАК Ссылка
	|ИЗ
	|	Справочник.LM_Абонемент КАК LM_Абонемент
	|ГДЕ
	|	LM_Абонемент.Активный";	
	РезультатЗапроса = Запрос.Выполнить().Выгрузить();
	
	Для Каждого Аб из РезультатЗапроса Цикл
		
		// Возобновление приостановленного абонемента
		Если Аб.Ссылка.Приостановка и НачалоДня(Аб.Ссылка.ДатаВозобновления) <= ТекущаяДата() Тогда
			
			Попытка
				Об = Аб.Ссылка.ПолучитьОбъект();
				Об.Приостановка = Ложь;
				Об.Записать();
			Исключение
				// Ошибка блокировки объекта
			КонецПопытки;
			
		КонецЕсли;
		
		// Делаем неактивным (окончен срок абонемента)
		Если НачалоДня(Аб.Ссылка.ДатаОкончания) <= ТекущаяДата() Тогда
			
			Попытка
				Об = Аб.Ссылка.ПолучитьОбъект();
				Об.Активный = Ложь;
				Об.Записать();
			Исключение
				// Ошибка блокировки объекта
			КонецПопытки;
			
		КонецЕсли;
		
	КонецЦикла;	
	
КонецПроцедуры

Функция ПолучитьОповещения() Экспорт 

	МассивОповещений = Новый Массив;
	
	С = Новый Структура;
	
	МассивПользователей = Новый Массив;
	МассивПользователей.Добавить(ПользователиКлиентСервер.ТекущийПользователь());
	МассивПользователей.Добавить(Справочники.Пользователи.ПустаяСсылка());
	
	Запрос = Новый Запрос;
	Запрос.Текст = 
	"ВЫБРАТЬ
	|	LM_Оповещения.Источник КАК Источник,
	|	LM_Оповещения.ВремяСобытия КАК ВремяСобытия,
	|	LM_Оповещения.Пользователь КАК Пользователь,
	|	LM_Оповещения.Завершено КАК Завершено,
	|	LM_Оповещения.СрокНапоминания КАК СрокНапоминания,
	|	LM_Оповещения.Описание КАК Описание
	|ИЗ
	|	РегистрСведений.LM_Оповещения КАК LM_Оповещения
	|ГДЕ
	|	LM_Оповещения.Пользователь В(&Пользователи)
	|	И НЕ LM_Оповещения.Завершено";
	Запрос.УстановитьПараметр("Пользователи", МассивПользователей);
	Оповещения = Запрос.Выполнить().Выгрузить();
	Для Каждого Оп из Оповещения Цикл
		
		С.Вставить("Описание",Оп.Описание);
		С.Вставить("Источник",Оп.Источник);
		
		Струк = новый Структура("Источник, Описание, ВремяСобытия, Пользователь, Завершено, СрокНапоминания", 
		Оп.Источник, Оп.Описание, Оп.ВремяСобытия, Оп.Пользователь, Оп.Завершено, Оп.СрокНапоминания,);
		КлючЗаписи = РегистрыСведений.LM_Оповещения.СоздатьКлючЗаписи(Струк);
		С.Вставить("КлючЗаписи",КлючЗаписи);

		МассивОповещений.Добавить(С);
		
	КонецЦикла;
	
	Возврат МассивОповещений;

КонецФункции

