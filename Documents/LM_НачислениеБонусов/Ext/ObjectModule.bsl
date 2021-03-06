﻿
Процедура ОбработкаПроведения(Отказ, Режим)
	
	//КолСекунд = -(Дата("01.01.0001 0:00:00") - КоличествоЧасов);
	
	// регистр ДвижениеДисконтныхКарт Приход
	Движения.LM_ДвижениеДисконтныхКарт.Записывать = Истина;
	Для Каждого Стр из ДисконтныеКарты Цикл
		Движение = Движения.LM_ДвижениеДисконтныхКарт.Добавить();
		Движение.ВидДвижения 		= ВидДвиженияНакопления.Приход;
		Движение.Период 			= Дата;
		Движение.Клиент 			= Стр.ДисконтнаяКарта.Владелец;
		Движение.ДисконтнаяКарта 	= Стр.ДисконтнаяКарта;
		Движение.СуммаБонусов 		= Стр.СуммаБонусов;
		Движение.Организация		= Организация;
	КонецЦикла; 

КонецПроцедуры

Процедура ПередЗаписью(Отказ, РежимЗаписи, РежимПроведения)
	
	Если НЕ ЗначениеЗаполнено(ЭтотОбъект.АвторДокумента) Тогда
		ЭтотОбъект.АвторДокумента = ПользователиКлиентСервер.ТекущийПользователь();
	КонецЕсли;
	
	Сумма = ДисконтныеКарты.Итог("СуммаБонусов");

КонецПроцедуры

Процедура ПриКопировании(ОбъектКопирования)
	 АвторДокумента = Неопределено;
	 Комментарий    = Неопределено;
КонецПроцедуры
