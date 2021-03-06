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

// Проверияет образовавшуюся задолженность
Процедура ПроверкаЗадолженности() Экспорт 

	Настройки = ПолучитьНастройки();
	
	Если Настройки.ИспользоватьОповещения и Настройки.ОповещатьОЗадолженности <> 0 Тогда
		
		Запрос = Новый Запрос;
		Запрос.Текст = 
		"ВЫБРАТЬ
		|	LM_СписанияСуммЗаУрокиОстаткиИОбороты.Клиент КАК Клиент,
		|	LM_СписанияСуммЗаУрокиОстаткиИОбороты.СуммаКонечныйОстаток КАК Остаток
		|ИЗ
		|	РегистрНакопления.LM_СписанияСуммЗаУроки.ОстаткиИОбороты КАК LM_СписанияСуммЗаУрокиОстаткиИОбороты
		|ГДЕ
		|	LM_СписанияСуммЗаУрокиОстаткиИОбороты.СуммаКонечныйОстаток < 0";
		Должники = Запрос.Выполнить().Выгрузить();
		Для Каждого Стр из Должники Цикл		
			
			//ПроверитьИДобавитьВОповещения();
			
			НовЗапись = РегистрыСведений.LM_Оповещения.СоздатьМенеджерЗаписи();
			НовЗапись.ВремяСобытия = ТекущаяДата();
			НовЗапись.Источник = Должники.Клиент;
			НовЗапись.Описание = "Задолженность на " +ТекущаяДата()+ ": " +Формат(Должники.Остаток,"ЧДЦ=2");
			НовЗапись.Пользователь = Неопределено;
			НовЗапись.СрокНапоминания = НачалоДня(ТекущаяДата()) + 86400; //86400 = 1 день
			НовЗапись.Записать();
		КонецЦикла;
		
	КонецЕсли;
	
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

Функция ПолучитьНастройки() Экспорт 
	Возврат РегистрыСведений.LM_Настройки.ПолучитьПоследнее(ТекущаяДата());
КонецФункции
