﻿Процедура ПередЗаписью(Отказ, РежимЗаписи, РежимПроведения)
	
	Если НЕ ПометкаУдаления Тогда
		
		//Округление секунд
		Минута = ?(Минута(Дата)=0,1,Минута(Дата));
		НоваяДата = НачалоЧаса(Дата) + (60*Минута);
		
		Если НЕ ЗначениеЗаполнено(ЭтотОбъект.АвторДокумента) Тогда
			ЭтотОбъект.АвторДокумента = ПользователиКлиентСервер.ТекущийПользователь();
		КонецЕсли;     	
		
		Если ЗначениеЗаполнено(ГруппаОбучения) и ПроверкаНаКорректностьВыбраннойГруппыОбучения() Тогда
			Отказ = Истина;
		КонецЕсли;
		
		Документы.LM_Урок.РассчитатьТабличнуюЧасть(ЭтотОбъект);	
		
		Если РежимЗаписи = РежимЗаписиДокумента.Проведение и ЗначениеЗаполнено(Педагог) Тогда
			
			НомерБезНулей = Ссылка.Номер;
			Пока Найти(НомерБезНулей,"0") = 1 Цикл
				НомерБезНулей = Сред(НомерБезНулей,2); //удаляет лидирующие нули
			КонецЦикла; 
			
			ИтогПроверки = ПроверитьДокументПоГрафикуРабочегоВремени();
			Если ИтогПроверки <> Неопределено Тогда 	
				ТекстСообщения = "Урок №"+НомерБезНулей+ " от " +Формат(Ссылка.Дата,"ДФ=dd.MM.yyyy")+ " с " +Формат(Ссылка.Дата,"ДФ=HH:mm")+ 
				" по " +Формат(Ссылка.Дата-('00010101'-Ссылка.КоличествоЧасов),"ДФ=HH:mm") + " не входит в график учета рабочего времени педагога " 
				+ИтогПроверки.Педагог+ " (" +Формат(ИтогПроверки.Дата,"ДФ='ММММ гггг ""г"".'")+ ")!!!";
				ОбщегоНазначенияКлиентСервер.СообщитьПользователю(ТекстСообщения);
			КонецЕсли;
			
			
			//Пересечение проверяется с подобными по периоду начала и окончания урока и Педагогу
			ДокументПересечения = ДокументПересекаетсяСДругими();
			Если ДокументПересечения <> Неопределено Тогда
				
				НомерБезНулей2 = ДокументПересечения.Номер;
				Пока Найти(НомерБезНулей2,"0") = 1 Цикл
					НомерБезНулей2 = Сред(НомерБезНулей2,2); //удаляет лидирующие нули
				КонецЦикла;
				
				ТекстСообщения = "Урок №"+НомерБезНулей+ " от " +Формат(Ссылка.Дата,"ДФ=dd.MM.yyyy")+ " с " +Формат(Ссылка.Дата,"ДФ=HH:mm")+ 
				" по " +Формат(Ссылка.Дата-('00010101'-Ссылка.КоличествоЧасов),"ДФ=HH:mm")+ " пересекается по времени с уроком №"+НомерБезНулей2+ 
				" с " +Формат(ДокументПересечения.Дата,"ДФ=HH:mm")+	" по " +Формат(ДокументПересечения.Дата-('00010101'-ДокументПересечения.КоличествоЧасов),"ДФ=HH:mm")+ " "
				+ ?(Ссылка.Педагог = ДокументПересечения.Педагог, "по педагогу: " +ДокументПересечения.Педагог+ "!!!","")
				+ ?(Ссылка.Помещение = ДокументПересечения.Помещение, "по помещению: " +ДокументПересечения.Помещение+ "!!!","");
				ОбщегоНазначенияКлиентСервер.СообщитьПользователю(ТекстСообщения);
				
			КонецЕсли;		
			
		КонецЕсли;
		
		Окончание = Дата - ('00010101'-КоличествоЧасов);
		
		Документы.LM_Урок.ПересчитатьНачисленияПедагога(ЭтотОбъект,Ложь);
		
		НачисленоПедагогу = НачисленияПедагогу.Итог("СуммаНачисления");
		СуммаБонусов = Ученики.Итог("СуммаБонусов");
		Сумма 		= Ученики.Итог("Сумма");
		СуммаСкидки = Ученики.Итог("Скидка");
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
		
		// регистр СписанияСуммЗаУроки Расход 		
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
		Движение.Скидка  	 		= Стр.Коэффициент;
		Движение.ГруппаОбучения 	= ГруппаОбучения;
		Движение.Организация 		= Организация;
		Движение.Явка				= Стр.Явка;
		
		Если ЗначениеЗаполнено(Стр.ДисконтнаяКарта) Тогда
			
			Если ЗначениеЗаполнено(Стр.ДисконтнаяКарта.ДатаОкончанияДействия) и Дата > КонецДня(Стр.ДисконтнаяКарта.ДатаОкончанияДействия) Тогда
				Отказ = Истина;
				Сообщение = Новый СообщениеПользователю;
				Сообщение.Текст = "У дисконтной карты: " +Стр.ДисконтнаяКарта+ " истек срок действия! Действительна по " +Формат(Стр.ДисконтнаяКарта.ДатаОкончанияДействия,"ДФ=dd.MM.yyyy");
				Сообщение.Сообщить();
			КонецЕсли;
			
			// регистр ДвижениеДисконтныхКарт Расход 		
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
	
	Для Каждого Стр из НачисленияПедагогу Цикл 		
		Если ЗначениеЗаполнено(Стр.СуммаНачисления) Тогда
			// регистр LM_РасчетыПоЗарплате Приход 		
			Движения.LM_РасчетыПоЗарплате.Записывать = Истина;
			Движение = Движения.LM_РасчетыПоЗарплате.Добавить();
			Движение.ВидДвижения 		= ВидДвиженияНакопления.Приход;
			Движение.Период 	 		= Дата;
			Движение.Педагог 	 		= Педагог;
			Движение.Ученик  	 		= Стр.Ученик;
			Движение.Сумма				= Стр.СуммаНачисления;
			Движение.НеИзменять 		= Стр.НеИзменять;
			Движение.Организация 		= Организация;
			Движение.ПредметОбучения 	= ПредметОбучения;
			Движение.Комментарий 		= Стр.Комментарий;
		КонецЕсли;		
	КонецЦикла;	
	
КонецПроцедуры 

Процедура ПриКопировании(ОбъектКопирования)
	
	АвторДокумента = Неопределено;
	Комментарий    = Неопределено;
	
	НачисленияПедагогу.Очистить();
	
	Ученики.Очистить();	
	Для Каждого стр из ОбъектКопирования.Ученики Цикл		
		НовУч = Ученики.Добавить();
		НовУч.Ученик = Стр.Ученик;
		НовУч.Тариф = Стр.Тариф;
		НовУч.ДисконтнаяКарта = Стр.ДисконтнаяКарта;
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

