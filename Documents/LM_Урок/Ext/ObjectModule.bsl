﻿Процедура ПередЗаписью(Отказ, РежимЗаписи, РежимПроведения)
	
	// Убираем секунды из даты
	Если Дата <> НачалоМинуты(Дата) Тогда
		Дата = НачалоМинуты(Дата);
	КонецЕсли;
		
	Если ЭтоНовый() и Организация.Пустая() Тогда		
		LMНастроки = РегистрыСведений.LM_Настройки.ПолучитьПоследнее(ТекущаяДата());
		Организация = LMНастроки.Организация;
	КонецЕсли;

	Если НЕ ПометкаУдаления Тогда
		
		Если НЕ ЗначениеЗаполнено(ЭтотОбъект.АвторДокумента) Тогда
			ЭтотОбъект.АвторДокумента = ПользователиКлиентСервер.ТекущийПользователь();
		КонецЕсли;     	
		
		Если ЗначениеЗаполнено(ГруппаОбучения) и ПроверкаНаКорректностьВыбраннойГруппыОбучения() Тогда
			Отказ = Истина;
		КонецЕсли;
		
		Документы.LM_Урок.РассчитатьТабличнуюЧасть(ЭтотОбъект);
				
		Окончание = Дата - ('00010101'-КоличествоЧасов);
		
		Документы.LM_Урок.ПересчитатьНачисленияПедагога(ЭтотОбъект);
		
		НачисленоПедагогу 	= НачисленияПедагогу.Итог("СуммаНачисления");
		СуммаБонусов 		= Ученики.Итог("СуммаБонусов");
		Сумма 				= Ученики.Итог("Сумма");
		СуммаСкидки 		= Ученики.Итог("СуммаСкидки");
		СуммаДопРасходов 	= Расходы.Итог("Сумма");
				
	КонецЕсли;	
		
КонецПроцедуры

Функция ДокументПересекаетсяСДругими()                               	
	Возврат Документы.LM_Урок.ДокументПересекаетсяСДругими(ЭтотОбъект);	
КонецФункции     

Функция ПроверитьДокументПоГрафикуРабочегоВремени()                                 	
	Возврат Документы.LM_Урок.ПроверитьДокументПоГрафикуРабочегоВремени(ЭтотОбъект);	
КонецФункции

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
	
	Для Каждого Стр из Ученики Цикл
		
		Если НЕ Стр.Явка и НЕ Стр.СписатьОплату Тогда
			Продолжить;
		КонецЕсли;
		
		Если ЗначениеЗаполнено(Стр.Абонемент) Тогда
			Ответ = ПроверитьАбонемент(Стр);
			Если Ответ <> Неопределено Тогда
				Сообщение = Новый СообщениеПользователю;
				Сообщение.Текст = Ответ;
				Сообщение.Сообщить();
				Отказ = Истина;
			КонецЕсли;
		КонецЕсли;

		// Регистр СписанияСуммЗаУроки Расход 		
		Движения.LM_СписанияСуммЗаУроки.Записывать = Истина;
		Движение = Движения.LM_СписанияСуммЗаУроки.Добавить();
		Движение.ВидДвижения 		= ВидДвиженияНакопления.Расход;
		Движение.Период 	 		= Дата;
		Движение.Клиент 	 		= Стр.Ученик;
		Движение.Педагог 	 		= Педагог;
		Движение.ПредметОбучения 	= ПредметОбучения;
		Движение.Тариф  	 		= Стр.Тариф;
		Движение.Часы 		 		= -(Дата("01.01.0001 0:00:00") - КоличествоЧасов); //в секундах
		Движение.Сумма  	 		= Стр.Сумма;
		Движение.Скидка  	 		= Стр.Скидка;
		Движение.ГруппаОбучения 	= ГруппаОбучения;
		Движение.Организация 		= Организация;
		Движение.Явка				= Стр.Явка;
		Движение.Абонемент			= Стр.Абонемент;
		Движение.КоличествоУроков	= -1;
		Если Стр.Явка Тогда
			Движение.КоличествоЯвок		= -1;
		КонецЕсли;
		
		Если ЗначениеЗаполнено(Стр.ДисконтнаяКарта) Тогда
			
			Если ЗначениеЗаполнено(Стр.ДисконтнаяКарта.ДатаОкончанияДействия) и Дата > КонецДня(Стр.ДисконтнаяКарта.ДатаОкончанияДействия) Тогда
				Отказ = Истина;
				Сообщение = Новый СообщениеПользователю;
				Сообщение.Текст = "У дисконтной карты: " +Стр.ДисконтнаяКарта+ " истек срок действия! Действительна по " +Формат(Стр.ДисконтнаяКарта.ДатаОкончанияДействия,"ДФ=dd.MM.yyyy");
				Сообщение.Сообщить();
			КонецЕсли;
			
			// Регистр ДвижениеДисконтныхКарт Расход 		
			Движения.LM_ДвижениеДисконтныхКарт.Записывать = Истина;
			Движение = Движения.LM_ДвижениеДисконтныхКарт.Добавить();
			Движение.ВидДвижения 		= ВидДвиженияНакопления.Приход;
			Движение.Период 	 		= Дата;
			Движение.Клиент 	 		= Стр.Ученик;
			Движение.ДисконтнаяКарта	= Стр.ДисконтнаяКарта;
			Движение.СуммаБонусов  	 	= Стр.СуммаБонусов;
			Движение.Организация 		= Организация;
		КонецЕсли;
		
	КонецЦикла;
	
	// Регистр LM_РасчетыПоЗарплате Приход
	Для Каждого Стр из НачисленияПедагогу Цикл 		
		Если ЗначениеЗаполнено(Стр.СуммаНачисления) Тогда
			Движения.LM_РасчетыПоЗарплате.Записывать = Истина;
			Движение = Движения.LM_РасчетыПоЗарплате.Добавить();
			Движение.ВидДвижения 		= ВидДвиженияНакопления.Приход;
			Движение.Период 	 		= Дата;
			Движение.Педагог 	 		= Педагог;
			Движение.Сумма				= Стр.СуммаНачисления;
			Движение.НеИзменять 		= Стр.НеИзменять;
			Движение.Организация 		= Организация;
			Движение.Комментарий 		= Стр.Комментарий;
		КонецЕсли;		
	КонецЦикла;	
	
	// Регистр LM_Расходы Приход
	Для Каждого Стр из Расходы Цикл		 		
		Движения.LM_Расходы.Записывать = Истина;
		Движение = Движения.LM_Расходы.Добавить();
		Движение.ВидДвижения 		= ВидДвиженияНакопления.Расход;
		Движение.Период 	 		= Дата;
		Движение.Сумма				= Стр.Сумма;
		Движение.Организация 		= Организация;
		Движение.СтатьяЗатрат 		= Стр.СтатьяЗатрат;
	КонецЦикла;
	
	Документы.LM_Урок.ПроверкаПересечений(ЭтотОбъект);
	
КонецПроцедуры

Функция ПроверитьАбонемент(Стр)
	
	Если НЕ ЗначениеЗаполнено(Стр.Абонемент.ДатаАктивации) Тогда
		
		Возврат "У ученика " +Стр.Ученик+ " не активен абонемент: " +Стр.Абонемент+ " строка: " +Стр.НомерСтроки;
		
	Иначе
		
		Если Стр.Абонемент.ДатаНачала > НачалоДня(Дата) Тогда
			Возврат "У ученика " +Стр.Ученик+ " дата начала абонемента больше даты урока! Строка: " +Стр.НомерСтроки;
		ИначеЕсли Стр.Абонемент.ДатаОкончания < НачалоДня(Дата) Тогда
			Возврат "У ученика " +Стр.Ученик+ " дата окончания абонемента меньше даты урока! Строка: " +Стр.НомерСтроки;			
		КонецЕсли;
		
		Для Каждого СтрПриостановка из Стр.Абонемент.Приостановки Цикл 			
			Если НачалоДня(Дата) > СтрПриостановка.ДатаПриостановки и КонецДня(Дата) < СтрПриостановка.ДатаВозобновления Тогда
				Возврат "" +Ссылка+ " - На " +Формат(Дата,"ДФ=dd.MM.yy")+ " у ученика " +Стр.Ученик+ " приостановлен абонемент: " +Стр.Абонемент+ " строка: " +Стр.НомерСтроки;
				Прервать;
			КонецЕсли;			
		КонецЦикла;
		
		// Проверить оплату абонемента
		Запрос = Новый Запрос;
		Запрос.Текст = 
		"ВЫБРАТЬ
		|	LM_СписанияСуммЗаУрокиОстатки.КоличествоУроковОстаток КАК УрокиОстаток,
		|	LM_СписанияСуммЗаУрокиОстатки.ЧасыОстаток КАК ЧасыОстаток
		|ИЗ
		|	РегистрНакопления.LM_СписанияСуммЗаУроки.Остатки КАК LM_СписанияСуммЗаУрокиОстатки
		|ГДЕ
		|	LM_СписанияСуммЗаУрокиОстатки.Абонемент = &Абонемент";
		Запрос.УстановитьПараметр("Абонемент", Стр.Абонемент);
		РезультатЗапроса = Запрос.Выполнить().Выгрузить();
		
		Если РезультатЗапроса.Количество() = 0 Тогда
			Если ЗначениеЗаполнено(Стр.Абонемент.КоличествоЗанятий) Тогда
				Если Стр.Абонемент.КоличествоЗанятий < 1 Тогда
					Возврат "" +Ссылка+ " - нехватает остатков уроков по абонементу: " +Стр.Абонемент+ " строка: " +Стр.НомерСтроки;
				КонецЕсли;
			ИначеЕсли ЗначениеЗаполнено(Стр.Абонемент.КоличествоЧасов) Тогда
				Разница = Стр.Абонемент.КоличествоЧасов - (-('00010101' - КоличествоЧасов)/60/60); 
				Если Разница < 0 Тогда
					Возврат "" +Ссылка+ " - нехватает " +Формат(-Разница,"ЧДЦ=1")+ " остатков часов по абонементу: " +Стр.Абонемент+ " строка: " +Стр.НомерСтроки;
				КонецЕсли;
			КонецЕсли;			
		КонецЕсли;
		
		
		Для Каждого СтрОст из РезультатЗапроса Цикл
			Если ЗначениеЗаполнено(Стр.Абонемент.КоличествоЗанятий) Тогда
				Если Стр.Абонемент.КоличествоЗанятий-СтрОст.УрокиОстаток < 1 Тогда
					Возврат "" +Ссылка+ " - нехватает остатков уроков по абонементу: " +Стр.Абонемент+ " строка: " +Стр.НомерСтроки;
				КонецЕсли;
			ИначеЕсли ЗначениеЗаполнено(Стр.Абонемент.КоличествоЧасов) Тогда
				Разница = Стр.Абонемент.КоличествоЧасов-(-СтрОст.ЧасыОстаток/60/60) - (-('00010101' - КоличествоЧасов)/60/60); 
				Если Разница < 0 Тогда
					Возврат "" +Ссылка+ " - нехватает " +Формат(-Разница,"ЧДЦ=1")+ " остатков часов по абонементу: " +Стр.Абонемент+ " строка: " +Стр.НомерСтроки;
				КонецЕсли;
			КонецЕсли;
		КонецЦикла;
						
	КонецЕсли;	
	
	Возврат Неопределено;
	
КонецФункции

Процедура ПриКопировании(ОбъектКопирования)
	
	АвторДокумента = Неопределено;
	Комментарий    = Неопределено;
	
	НачисленияПедагогу.Очистить();
	Расходы.Очистить();
	
	Ученики.Очистить();	
	Для Каждого стр из ОбъектКопирования.Ученики Цикл		
		НовУч = Ученики.Добавить();
		НовУч.Ученик 			= Стр.Ученик;
		НовУч.Тариф 			= Стр.Тариф;
		НовУч.ДисконтнаяКарта 	= Стр.ДисконтнаяКарта;
	КонецЦикла;	
	
	Если Не ЗначениеЗаполнено(ОбъектКопирования.Организация) Тогда
		LMНастроки = РегистрыСведений.LM_Настройки.ПолучитьПоследнее(ТекущаяДата());
		ЗаполнитьЗначенияСвойств(ЭтотОбъект, LMНастроки);
	КонецЕсли;
	
КонецПроцедуры

Функция ПроверкаНаКорректностьВыбраннойГруппыОбучения()
	
	ЕстьОграничения = Ложь;
	Для Каждого Стр из Ученики Цикл
		
		Если НЕ Стр.Ученик.ТолькоВыбранныеГруппыОбучения Тогда
			Продолжить;
		КонецЕсли;
		
		ПарметрыОтбора = Новый Структура;
		ПарметрыОтбора.Вставить("ГруппаОбучения",ГруппаОбучения);
		НайденныеГруппы = Стр.Ученик.ГруппыОбучения.НайтиСтроки(ПарметрыОтбора);
		Если НайденныеГруппы.Количество() > 0 Тогда
			Для Каждого СтрГр из НайденныеГруппы Цикл
				Если Дата > КонецДня(СтрГр.ДатаОкончания) Тогда
					Сообщить(""+Ссылка+ " для ученика " +Стр.Ученик+ " окончен срок группы " +КонецДня(СтрГр.ДатаОкончания)+ " " +ГруппаОбучения+ "!");
					ЕстьОграничения = Истина;
				КонецЕсли;
			КонецЦикла;
		Иначе
			Сообщить(""+Ссылка+ " для ученика " +Стр.Ученик+ " не разрешена группа " +ГруппаОбучения+ "!");
			ЕстьОграничения = Истина;			
		КонецЕсли;
		
	КонецЦикла;	
	
	Возврат ЕстьОграничения;
	
КонецФункции

Процедура ОбработкаЗаполнения(ДанныеЗаполнения, ТекстЗаполнения, СтандартнаяОбработка)
	
	Если ЭтоНовый() Тогда		
		LMНастроки = РегистрыСведений.LM_Настройки.ПолучитьПоследнее(ТекущаяДата());
		ЗаполнитьЗначенияСвойств(ЭтотОбъект, LMНастроки);
	КонецЕсли;
	
КонецПроцедуры

