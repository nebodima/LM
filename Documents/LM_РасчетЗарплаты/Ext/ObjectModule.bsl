﻿
Процедура ПередЗаписью(Отказ, РежимЗаписи, РежимПроведения)
	
	Если НЕ ЗначениеЗаполнено(АвторДокумента) Тогда
		АвторДокумента = ПользователиКлиентСервер.ТекущийПользователь();
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

Процедура ОбработкаПроведения(Отказ, РежимПроведения)
	
	// регистр LM_РасчетыПоЗарплате Приход 		
	Движения.LM_РасчетыПоЗарплате.Записывать = Истина;
	Движение = Движения.LM_РасчетыПоЗарплате.Добавить();
	Движение.ВидДвижения 		= ВидДвиженияНакопления.Приход;
	Движение.Период 	 		= КонецДня(ДатаОкончания);
	Движение.Педагог 	 		= Педагог;
	Движение.ЗП					= СуммаДокумента;
	Движение.Организация		= Организация;
	
	// регистр LM_РасчетыПоЗарплате Расход 		
	Движения.LM_РасчетыПоЗарплате.Записывать = Истина;
	Движение = Движения.LM_РасчетыПоЗарплате.Добавить();
	Движение.ВидДвижения 		= ВидДвиженияНакопления.Расход;
	Движение.Период 	 		= КонецДня(ДатаОкончания);
	Движение.Педагог 	 		= Педагог;
	Движение.ЗП					= СуммаДокумента;
	Движение.Организация		= Организация;
	
КонецПроцедуры
