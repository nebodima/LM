﻿
// Формирует печатные формы.
//
// Параметры:
//  МассивОбъектов – Массив – ссылки на объекты, которые нужно распечатать;
//  ПараметрыПечати – Структура – дополнительные настройки печати;
//  КоллекцияПечатныхФорм – ТаблицаЗначений – сформированные табличные документы (выходной параметр)
//  ОбъектыПечати – СписокЗначений – значение – ссылка на объект;
//                                            представление – имя области, в которой был выведен объект (выходной параметр);
//  ПараметрыВывода – Структура – дополнительные параметры сформированных табличных документов (выходной параметр).
//
Процедура Печать(МассивОбъектов, ПараметрыПечати, КоллекцияПечатныхФорм, ОбъектыПечати, ПараметрыВывода) Экспорт
	
	НужноПечататьМакет = УправлениеПечатью.НужноПечататьМакет(КоллекцияПечатныхФорм, "ПечатьПКО");
    Если НужноПечататьМакет Тогда
        УправлениеПечатью.ВывестиТабличныйДокументВКоллекцию(
        КоллекцияПечатныхФорм,
        "ПечатьПКО",
        НСтр("ru = 'Приходный кассовый ордер'"),
        ПечатьПКО(МассивОбъектов, ОбъектыПечати),
        ,
        "Документ.ПриходныйКассовыйОрдер.ПечатьПКО");
    КонецЕсли;
	
КонецПроцедуры 

Функция ПечатьПКО(МассивОбъектов, ОбъектыПечати)
	
	ТабличныйДокумент = Новый ТабличныйДокумент;
	Макет = Документы.ПриходныйКассовыйОрдер.ПолучитьМакет("ПечатьПКО");
	Запрос = Новый Запрос;
	Запрос.Текст =
	"ВЫБРАТЬ
	|	ПКО.АвторДокумента КАК АвторДокумента,
	|	ПКО.ВидОперации КАК ВидОперации,
	|	ПКО.Дата КАК Дата,
	|	ПКО.ДокументОснования КАК ДокументОснования,
	|	ПКО.Касса КАК Касса,
	|	ПКО.LM_ФизЛицо КАК Контрагент,
	|	ПКО.Комментарий КАК Комментарий,
	|	ПКО.НазначениеПлатежа КАК НазначениеПлатежа,
	|	ПКО.Номер КАК Номер,
	|	ПКО.СуммаДокумента КАК СуммаДокумента,
	|	ПКО.Родитель КАК Родитель,
	|	ПКО.Подразделение КАК Подразделение,
	|	ПКО.Организация КАК Организация
	|ИЗ
	|	Документ.ПриходныйКассовыйОрдер КАК ПКО
	|ГДЕ
	|	ПКО.Ссылка В(&Ссылка)";
	Запрос.Параметры.Вставить("Ссылка", МассивОбъектов);
	Выборка = Запрос.Выполнить().Выбрать();
	
	Шапка = Макет.ПолучитьОбласть("Шапка");
	ТабличныйДокумент.Очистить();
	
	ВставлятьРазделительСтраниц = Ложь;
	
	Пока Выборка.Следующий() Цикл
		
		Если ВставлятьРазделительСтраниц Тогда
			ТабличныйДокумент.ВывестиГоризонтальныйРазделительСтраниц();
		КонецЕсли;
		
		Если ЗначениеЗаполнено(Выборка.СуммаДокумента) Тогда
			Сумма = Выборка.СуммаДокумента;
		Иначе
			Сумма = Выборка.СуммаБонусов;
		КонецЕсли;		
		
		Шапка.Параметры.Заполнить(Выборка);
		Шапка.Параметры.СуммаРубКоп       = Формат(Сумма, "ЧЦ=15; ЧДЦ=2");    
		Шапка.Параметры.Сумма             = Формат(Сумма, "ЧЦ=15; ЧДЦ=2");
		Шапка.Параметры.СуммаПрописью     = ЧислоПрописью(Сумма,,"рубль, рубля, рублей, м, копейка, копейки, копеек, ж, 2");
		Шапка.Параметры.ОрганизацияПоОКПО = "";
		Шапка.Параметры.ДатаДокумента     = Выборка.Дата;
		Шапка.Параметры.НомерДокумента    = ПрефиксацияОбъектовКлиентСервер.НомерНаПечать(Выборка.Номер, Истина, Ложь);
		Шапка.Параметры.ПринятоОт		  = ?(ЗначениеЗаполнено(Выборка.Родитель),Выборка.Родитель,Выборка.Контрагент);
		Шапка.Параметры.Основание		  = Выборка.НазначениеПлатежа;
	
		Шапка.Параметры.КодДебета 		  = "50.01";
		Шапка.Параметры.СубСчет   		  = "62.01, 62.02";
		
		Если ЗначениеЗаполнено(Выборка.Организация) Тогда
			Шапка.Параметры.ПредставлениеОрганизации = Выборка.Организация.Наименование;
		КонецЕсли;
		
		Шапка.Параметры.ПредставлениеПодразделения = Выборка.Подразделение;
		
		ТабличныйДокумент.Вывести(Шапка, Выборка.Уровень());
		
		ВставлятьРазделительСтраниц = Истина;
		
	КонецЦикла;
	
	Возврат ТабличныйДокумент;
КонецФункции

Процедура ОбработкаПолученияПредставления(Данные, Представление, СтандартнаяОбработка)
	
	СтандартнаяОбработка = Ложь;
	
	Номер = Данные.Номер;
	Пока Лев(Номер, 1) = "0" Цикл 
		Номер = Прав(Номер, СтрДлина(Номер) - 1);
	КонецЦикла;

	Представление = "ПКО (оплата+) " +Номер+ " от " +Формат(Данные.Дата,"ДФ=д.ММ.гггг")+ " " +Данные.Ссылка.ПредметОбучения;	
	
КонецПроцедуры
