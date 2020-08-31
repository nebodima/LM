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
	
	// регистр Касса Расход
	Движения.LM_Касса.Записывать = Истина;
	Движение = Движения.LM_Касса.Добавить();
	Движение.ВидДвижения = ВидДвиженияНакопления.Расход;
	Движение.Период 	 = Дата;
	Движение.Клиент 	 = LM_ФизЛицо;
	Движение.Сумма 		 = СуммаДокумента;
	Движение.Касса		 = Касса;
	Движение.ВидОперации = ВидОперации;
	Движение.ПредметОбучения = ПредметОбучения;
	Движение.СтатьяЗатрат = СтатьяЗатрат;
	Движение.Организация = Организация;
	
	Если ВидОперации = Перечисления.LM_ВидыОпераций.КассаУченики Тогда
		// регистр СписанияСуммЗаУроки 
		Движения.LM_СписанияСуммЗаУроки.Записывать = Истина;
		Движение = Движения.LM_СписанияСуммЗаУроки.Добавить();
		Движение.ВидДвижения = ВидДвиженияНакопления.Расход;
		Движение.Период 	 = Дата;
		Движение.Клиент 	 = LM_ФизЛицо;
		Движение.Сумма  	 = СуммаДокумента;
		Движение.ПредметОбучения    = ПредметОбучения;
		Движение.Организация = Организация;
		
		Если ЗначениеЗаполнено(ДокументОснования) Тогда
			//Движение.Педагог = ДокументОснования.Педагог;
			
			СтрокаУченика = ДокументОснования.Ученики.Найти(LM_ФизЛицо,"Ученик");
			Если ЗначениеЗаполнено(СтрокаУченика) Тогда
				Движение.Тариф = СтрокаУченика.Тариф;
				Движение.Часы  = -('00010101' - ДокументОснования.КоличествоЧасов);
			КонецЕсли;
			
		КонецЕсли;
		
	ИначеЕсли ВидОперации = Перечисления.LM_ВидыОпераций.ВнутренняяКасса Тогда		
		// регистр LM_РасчетыПоЗарплате Расход 		
		Движения.LM_РасчетыПоЗарплате.Записывать = Истина;
		Движение = Движения.LM_РасчетыПоЗарплате.Добавить();
		Движение.ВидДвижения 		= ВидДвиженияНакопления.Расход;
		Движение.Период 	 		= Дата;
		Движение.Педагог 	 	= LM_ФизЛицо;
		Движение.Сумма				= СуммаДокумента;
		Движение.Организация		= Организация;
	КонецЕсли;	

КонецПроцедуры

Процедура ПередЗаписью(Отказ, РежимЗаписи, РежимПроведения)
	
	Если НЕ ЗначениеЗаполнено(ЭтотОбъект.АвторДокумента) Тогда
		ЭтотОбъект.АвторДокумента = ПользователиКлиентСервер.ТекущийПользователь();
	КонецЕсли;	
		
КонецПроцедуры

Процедура ПриКопировании(ОбъектКопирования)
	
	АвторДокумента = Неопределено;
	Комментарий    = Неопределено;
	
	Если Не ЗначениеЗаполнено(ОбъектКопирования.Организация) Тогда
		LMНастроки = РегистрыСведений.LM_Настройки.ПолучитьПоследнее(ТекущаяДата());
		ЗаполнитьЗначенияСвойств(ЭтотОбъект, LMНастроки);
	КонецЕсли;

КонецПроцедуры

Процедура ОбработкаЗаполнения(ДанныеЗаполнения, ТекстЗаполнения, СтандартнаяОбработка)
	
	Если ЭтоНовый() Тогда
		LMНастроки = РегистрыСведений.LM_Настройки.ПолучитьПоследнее(ТекущаяДата());
		ЗаполнитьЗначенияСвойств(ЭтотОбъект, LMНастроки);
	КонецЕсли;
	
КонецПроцедуры
