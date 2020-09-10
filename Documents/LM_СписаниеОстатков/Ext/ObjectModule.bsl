﻿
Процедура ОбработкаПроведения(Отказ, Режим)
	
	//КолСекунд = -(Дата("01.01.0001 0:00:00") - КоличествоЧасов);
	
	// регистр СписанияСуммЗаУроки Приход
	Движения.LM_СписанияСуммЗаУроки.Записывать = Истина;	
	Для Каждого Стр из ТЗСписания Цикл
		Движение = Движения.LM_СписанияСуммЗаУроки.Добавить();
		Движение.ВидДвижения = ВидДвиженияНакопления.Расход;
		Движение.Период 			= Дата;
		Движение.Клиент 			= Стр.Ученик;
		Движение.Педагог 			= Стр.Педагог;
		Движение.Часы 				= Стр.КоличествоЧасов;
		Движение.Сумма 				= Стр.Сумма;
		Движение.Тариф 				= Стр.Тариф;
		Движение.ПредметОбучения 	= Стр.ПредметОбучения;
		Движение.ГруппаОбучения 	= Стр.ГруппаОбучения;
		Движение.Организация 		= Организация;
	КонецЦикла;
	
	// регистр ДвижениеДисконтныхКарт Приход
	Движения.LM_ДвижениеДисконтныхКарт.Записывать = Истина;
	Для Каждого Стр из ДисконтныеКарты Цикл
		Движение = Движения.LM_ДвижениеДисконтныхКарт.Добавить();
		Движение.ВидДвижения 		= ВидДвиженияНакопления.Расход;
		Движение.Период 			= Дата;
		Движение.Клиент 			= Стр.ДисконтнаяКарта.Владелец;
		Движение.ДисконтнаяКарта 	= Стр.ДисконтнаяКарта;
		Движение.СуммаБонусов 		= Стр.СуммаБонусов;
		Движение.Организация 		= Организация;
	КонецЦикла; 
	
	// регистр Касса Расход
	Движения.LM_Касса.Записывать = Истина;
	Для Каждого Стр из ТЗСписаниеКасса Цикл
		Движение = Движения.LM_Касса.Добавить();
		Движение.ВидДвижения = ВидДвиженияНакопления.Расход;
		Движение.Период 		= Дата;
		Движение.Клиент 		= Стр.Ученик;
		Движение.Касса 			= Стр.Касса;
		Движение.СтатьяЗатрат 	= Стр.СтатьяЗатрат; 		
		Движение.ПредметОбучения = Стр.ПредметОбучения;		
		Движение.ВидОперации 	= Стр.ВидОперации;		
		Движение.Сумма 			= Стр.Сумма;
		Движение.Организация 	= Организация;
	КонецЦикла;  

КонецПроцедуры

Процедура ПередЗаписью(Отказ, РежимЗаписи, РежимПроведения)
	
	Если НЕ ЗначениеЗаполнено(ЭтотОбъект.АвторДокумента) Тогда
		ЭтотОбъект.АвторДокумента = ПользователиКлиентСервер.ТекущийПользователь();
	КонецЕсли;
	
	Сумма = ТЗСписания.Итог("Сумма");
	СуммаБонусов = ДисконтныеКарты.Итог("СуммаБонусов");

КонецПроцедуры

Процедура ПриКопировании(ОбъектКопирования)
	 АвторДокумента = Неопределено;
	 Комментарий    = Неопределено;
КонецПроцедуры
