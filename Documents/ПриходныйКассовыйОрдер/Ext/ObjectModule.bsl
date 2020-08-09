﻿
Процедура ОбработкаПроведения(Отказ, Режим)
	
	LMНастроки = РегистрыСведений.LM_Настройки.ПолучитьПоследнее(ТекущаяДата());
	Если LMНастроки.Свойство("ДатаЗапретаРедактирования") Тогда 
		//Если ЗначениеЗаполнено(Организация) и ЗначениеЗаполнено(Организация.LM_ДатаЗапретаРедактирования) Тогда
		
		ДатаЗапрета = LMНастроки.ДатаЗапретаРедактирования;
		ТолькоНеделя = LMНастроки.ДатаЗапретаРедактированияНеделя;
		Если ЗначениеЗаполнено(ДатаЗапрета) Тогда
			Если Дата <= ДатаЗапрета	Тогда
				Отказ = Истина;
				Сообщить("Запрещено изменение документов ранее " +ДатаЗапрета);
				Возврат;
			КонецЕсли; 				
		КонецЕсли; 
		
		//Запрещено редактировать документы в закрытом периоде для Менеджеров
		Если ТолькоНеделя и РольДоступна("LM_Менеджер") и НЕ РольДоступна("ПолныеПрава")Тогда
			Отказ = Истина;
			Сообщить("Запрещено изменение документов ранее " +НачалоДня(НачалоДня(ТекущаяДата())-604800)+ " для Менеджеров");
			Возврат;
		КонецЕсли;
	КонецЕсли;
	
	// регистр Касса	
	Если ЗначениеЗаполнено(СуммаДокумента) Тогда
		Движения.LM_Касса.Записывать = Истина;
		Движение = Движения.LM_Касса.Добавить();
		Движение.ВидДвижения = ВидДвиженияНакопления.Приход;
		Движение.Период 	 = Дата;
		Движение.Клиент 	 = LM_ФизЛицо;
		Движение.Сумма  	 = СуммаДокумента;
		Движение.Касса 		 = Касса;
		Движение.ПредметОбучения = ПредметОбучения;
		Движение.ВидОперации = ВидОперации;
		Движение.СтатьяЗатрат = СтатьяЗатрат;
		Движение.Организация = Организация;
	КонецЕсли; 
	
	Если ВидОперации = Перечисления.LM_ВидыОпераций.КассаУченики и ЗначениеЗаполнено(СуммаДокумента) Тогда
		// регистр СписанияСуммЗаУроки 
		Движения.LM_СписанияСуммЗаУроки.Записывать = Истина;
		Движение = Движения.LM_СписанияСуммЗаУроки.Добавить();
		Движение.ВидДвижения = ВидДвиженияНакопления.Приход;
		Движение.Период 	 = Дата;
		Движение.Клиент 	 = LM_ФизЛицо;
		Движение.Сумма  	 = СуммаДокумента;
		Движение.Тариф		 = Тариф;
		Движение.ПредметОбучения = ПредметОбучения;
		Движение.Организация = Организация;
	КонецЕсли; 	          	
	
	Если ЗначениеЗаполнено(ДисконтнаяКарта) и ЗначениеЗаполнено(СуммаБонусов) Тогда
		
		Если ЗначениеЗаполнено(ДисконтнаяКарта.ДатаОкончанияДействия) и НачалоДня(ДисконтнаяКарта.ДатаОкончанияДействия) <= НачалоДня(Дата) Тогда
			Отказ = Истина;
			Сообщить("У дисконтной карты: " +ДисконтнаяКарта+ " истек срок действия!");
		КонецЕсли;
		
		ОстатокДоступныхБонусовИДенегПоКарте = ОпределитьОстатокДоступныхБонусовИДенег();
		Если ОстатокДоступныхБонусовИДенегПоКарте <> Неопределено Тогда
			
			Если СуммаБонусов > ОстатокДоступныхБонусовИДенегПоКарте.СуммаБонусовОстаток Тогда
				Отказ = Истина;
				Сообщить("Недостаточно бонусов для списания! ОстатокДоступныхБонусовПоКарте = " +ОстатокДоступныхБонусовИДенегПоКарте.СуммаБонусовОстаток);
			КонецЕсли;
		КонецЕсли;
		
		//СписаниеБонусов
		Если ЗначениеЗаполнено(СуммаБонусов) Тогда
			Движения.LM_ДвижениеДисконтныхКарт.Записывать = Истина;
			Движение = Движения.LM_ДвижениеДисконтныхКарт.Добавить();
			Движение.ВидДвижения 		= ВидДвиженияНакопления.Расход;
			Движение.Период 	 		= Дата;
			Движение.Клиент 	 		= ДисконтнаяКарта.Владелец;
			Движение.ДисконтнаяКарта 	= ДисконтнаяКарта;
			Движение.СуммаБонусов		= СуммаБонусов;
			Движение.Организация 		= Организация;
		КонецЕсли;
		
		// регистр СписанияСуммЗаУроки ОплачиваемБонусами
		Если ЗначениеЗаполнено(СуммаБонусов) Тогда
			Движения.LM_СписанияСуммЗаУроки.Записывать = Истина;
			Движение = Движения.LM_СписанияСуммЗаУроки.Добавить();
			Движение.ВидДвижения = ВидДвиженияНакопления.Приход;
			Движение.Период 	 = Дата;
			Движение.Клиент 	 = LM_ФизЛицо;
			Движение.Сумма  	 = СуммаБонусов;
			Движение.Тариф		 = Тариф;
			Движение.ПредметОбучения = ПредметОбучения;
			Движение.Организация = Организация;
		КонецЕсли;

	КонецЕсли;     	
	
КонецПроцедуры

Процедура ПередЗаписью(Отказ, РежимЗаписи, РежимПроведения)
	    	
	Если НЕ ЗначениеЗаполнено(ЭтотОбъект.АвторДокумента) Тогда
		ЭтотОбъект.АвторДокумента = ПользователиКлиентСервер.ТекущийПользователь();
	КонецЕсли;
	
КонецПроцедуры

Процедура ОбработкаЗаполнения(ДанныеЗаполнения, СтандартнаяОбработка)
		
	Если ЭтоНовый() Тогда
		LMНастроки = РегистрыСведений.LM_Настройки.ПолучитьПоследнее(ТекущаяДата());
		ЗаполнитьЗначенияСвойств(ЭтотОбъект, LMНастроки);
	КонецЕсли;

	
	Если ТипЗнч(ДанныеЗаполнения) = Тип("ДокументСсылка.LM_Урок") Тогда
		ДокументОснования = ДанныеЗаполнения.Ссылка;
		ВидОперации		  = Перечисления.LM_ВидыОпераций.КассаУченики;
		Организация 	  = ДанныеЗаполнения.Организация;
		ПредметОбучения	  = ДанныеЗаполнения.ПредметОбучения;
		
		//Если ДанныеЗаполнения.Ученики.Количество() > 0 Тогда
		//	Сумма = ДанныеЗаполнения.Ученики[0].Сумма;
		//КонецЕсли;
		
	ИначеЕсли ТипЗнч(ДанныеЗаполнения) = Тип("СправочникСсылка.LM_ФизЛица") Тогда
		
		ВидОперации	= Перечисления.LM_ВидыОпераций.КассаУченики;
		LM_ФизЛицо	= ДанныеЗаполнения.Ссылка;
		
		Если ЗначениеЗаполнено(ДанныеЗаполнения.Ссылка.Родитель1) Тогда
			Родитель = ДанныеЗаполнения.Ссылка.Родитель1;
		КонецЕсли;
		
	КонецЕсли;	
		
КонецПроцедуры

Функция ОпределитьОстатокДоступныхБонусовИДенег()
	
	Запрос = Новый Запрос;
	Запрос.Текст = 
	"ВЫБРАТЬ
	|	ДвижениеДисконтныхКартОстатки.СуммаБонусовОстаток КАК СуммаБонусовОстаток
	|ИЗ
	|	РегистрНакопления.LM_ДвижениеДисконтныхКарт.Остатки(, ) КАК ДвижениеДисконтныхКартОстатки
	|ГДЕ
	|	ДвижениеДисконтныхКартОстатки.ДисконтнаяКарта = &ДисконтнаяКарта";
	Запрос.УстановитьПараметр("ДисконтнаяКарта", ДисконтнаяКарта);
	
	РезультатЗапроса = Запрос.Выполнить();	
	ВыборкаДетальныеЗаписи = РезультатЗапроса.Выбрать();	
	Пока ВыборкаДетальныеЗаписи.Следующий() Цикл		
		С = Новый Структура;
		С.Вставить("СуммаБонусовОстаток",ВыборкаДетальныеЗаписи.СуммаБонусовОстаток);
		Возврат с;		
	КонецЦикла;
	
	Возврат Неопределено;
	
КонецФункции

Процедура ПриКопировании(ОбъектКопирования)
	
	АвторДокумента = Неопределено;
	Комментарий    = Неопределено;
	
	Если Не ЗначениеЗаполнено(ОбъектКопирования.Организация) Тогда
		LMНастроки = РегистрыСведений.LM_Настройки.ПолучитьПоследнее(ТекущаяДата());
		ЗаполнитьЗначенияСвойств(ЭтотОбъект, LMНастроки);
	КонецЕсли;
	
КонецПроцедуры

