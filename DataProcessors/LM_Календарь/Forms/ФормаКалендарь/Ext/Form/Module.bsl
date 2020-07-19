﻿
&НаСервере
Процедура ЗаполнитьНаСервере(ДатаНачала,ДатаОкончания)
	
	Планировщик.ТекущиеПериодыОтображения.Очистить();
	Планировщик.ТекущиеПериодыОтображения.Добавить(ДатаНачала, ДатаОкончания);
	
	// Инициализация элементов планировщика (записи по измерениям)
	ЭлементыПланировщика = Планировщик.Элементы;
	ЭлементыПланировщика.Очистить();
	
	Ур 	  = БиблиотекаКартинок.АктивныеПользователи;
	Напом = БиблиотекаКартинок.ВыполнитьЗадачу;  
	
	Запрос = Новый Запрос;
	Запрос.Текст = 
	"ВЫБРАТЬ
	|	Урок.Ссылка КАК Ссылка,
	|	Урок.Дата КАК Дата,
	|	Урок.КоличествоЧасов КАК КоличествоЧасов,
	|	Урок.Педагог КАК Педагог,
	|	Урок.Номер КАК Номер,
	|	Урок.Помещение КАК Помещение
	|ИЗ
	|	Документ.LM_Урок КАК Урок
	|ГДЕ
	|	Урок.Дата МЕЖДУ &ДатаНачала И &ДатаОкончания
	|	И Урок.Педагог = &Педагог
	|	И Урок.Помещение = &Помещение
	|	И Урок.ГруппаОбучения = &ГруппаОбучения
	|	И Урок.Проведен = ИСТИНА";
	
	Если НЕ ЗначениеЗаполнено(ФильтрПедагог) Тогда
		Запрос.Текст = СтрЗаменить(Запрос.Текст,"И Урок.Педагог = &Педагог","");
	КонецЕсли;              	
	
	Если НЕ ЗначениеЗаполнено(ФильтрПомещение) Тогда
		Запрос.Текст = СтрЗаменить(Запрос.Текст,"И Урок.Помещение = &Помещение","");
	КонецЕсли;
	
	Если НЕ ЗначениеЗаполнено(ФильтрГруппаОбучения) Тогда
		Запрос.Текст = СтрЗаменить(Запрос.Текст,"И Урок.ГруппаОбучения = &ГруппаОбучения","");
	КонецЕсли;
	
	Запрос.УстановитьПараметр("ДатаНачала", ДатаНачала);
	Запрос.УстановитьПараметр("ДатаОкончания", ДатаОкончания);
	Запрос.УстановитьПараметр("Педагог", ФильтрПедагог);
	Запрос.УстановитьПараметр("Помещение", ФильтрПомещение);
	Запрос.УстановитьПараметр("ГруппаОбучения", ФильтрГруппаОбучения);
	РезультатЗапроса = Запрос.Выполнить(); 	
	Уроки = РезультатЗапроса.Выбрать();
	
	Пока Уроки.Следующий() Цикл
		
		Начало  = Уроки.Дата;
		Конец   = Начало-('00010101'-Уроки.КоличествоЧасов);
		
		// Добавление новой записи в промежуток времени
		НовыйЭлемент = ЭлементыПланировщика.Добавить(Начало, Конец);
		Если ГруппаОбучения и ЗначениеЗаполнено(Уроки.Ссылка.ГруппаОбучения) Тогда
			НовыйЭлемент.Текст = НовыйЭлемент.Текст+"Группа: " +Уроки.Ссылка.ГруппаОбучения.Наименование+Символы.ПС;
		КонецЕсли;
		Если ПредметОбучения и ЗначениеЗаполнено(Уроки.Ссылка.ПредметОбучения) Тогда
			НовыйЭлемент.Текст = НовыйЭлемент.Текст+"Предмет: " +Уроки.Ссылка.ПредметОбучения.Наименование+Символы.ПС;
		КонецЕсли;
		Если Педагог и ЗначениеЗаполнено(Уроки.Ссылка.Педагог) Тогда
			НовыйЭлемент.Текст = НовыйЭлемент.Текст+"Педагог: " +Уроки.Ссылка.Педагог.Наименование+Символы.ПС;
		КонецЕсли;
		
		НовыйЭлемент.Текст = НовыйЭлемент.Текст+"Ученики: ";
		Для Каждого СтрУченик из Уроки.Ссылка.Ученики Цикл
			НовыйЭлемент.Текст = НовыйЭлемент.Текст+СтрУченик.Ученик.Наименование+Символы.ПС;
		КонецЦикла;
		НовыйЭлемент.Значение = Уроки.Ссылка;               		
		НовыйЭлемент.Картинка = Ур;
		
		
		НовыйЭлемент.ЦветФона = WebЦвета.СеребристоСерый;
		Попытка
			Если Цвет = "Помещение" Тогда
				Если ЗначениеЗаполнено(Уроки.Ссылка.Помещение) Тогда 
					НовыйЭлемент.ЦветФона = WebЦвета[СокрЛП(Уроки.Ссылка.Помещение.Цвет)];
				КонецЕсли;
			ИначеЕсли Цвет = "ПредмОбуч" Тогда
				Если ЗначениеЗаполнено(Уроки.Ссылка.ПредметОбучения) Тогда 
					НовыйЭлемент.ЦветФона = WebЦвета[СокрЛП(Уроки.Ссылка.ПредметОбучения.Цвет)];
				КонецЕсли;
			ИначеЕсли Цвет = "Педагог" Тогда
				Если ЗначениеЗаполнено(Уроки.Ссылка.Педагог) Тогда 
					НовыйЭлемент.ЦветФона = WebЦвета[СокрЛП(Уроки.Ссылка.Педагог.Цвет)];
				КонецЕсли;
			КонецЕсли;			
		Исключение
		КонецПопытки;		
		
	КонецЦикла;
	
	//Добавляем даты из графика Педагога
	Планировщик.ИнтервалыФона.Очистить();
	Если ЗначениеЗаполнено(ФильтрПедагог) Тогда
		
		Запрос = Новый Запрос;
		Запрос.Текст = 
		"ВЫБРАТЬ
		|	ГрафикРабочегоВремениПедагогаТЧ.Дата КАК Дата,
		|	ГрафикРабочегоВремениПедагогаТЧ.ВремяНачала КАК ВремяНачала,
		|	ГрафикРабочегоВремениПедагогаТЧ.ВремяОкончания КАК ВремяОкончания
		|ИЗ
		|	Документ.LM_ГрафикРабочегоВремениПедагога.ТЧ КАК ГрафикРабочегоВремениПедагогаТЧ
		|ГДЕ
		|	ГрафикРабочегоВремениПедагогаТЧ.Ссылка.Проведен
		|	И ГрафикРабочегоВремениПедагогаТЧ.Ссылка.Педагог = &Педагог
		|	И ГрафикРабочегоВремениПедагогаТЧ.Дата МЕЖДУ &ДатаНачала И &ДатаОкончания";	
		Запрос.УстановитьПараметр("Педагог", ФильтрПедагог);
		Запрос.УстановитьПараметр("ДатаНачала", НачалоМесяца(ДатаНачала));
		Запрос.УстановитьПараметр("ДатаОкончания", КонецМесяца(ДатаОкончания));
		РезультатЗапроса = Запрос.Выполнить(); 	
		ВыборкаДетальныеЗаписи = РезультатЗапроса.Выбрать();
		                   		
		Пока ВыборкаДетальныеЗаписи.Следующий() Цикл
			// Добавление новой записи в промежуток времени
			ВыбДатаНачала = ВыборкаДетальныеЗаписи.Дата -('00010101' - ВыборкаДетальныеЗаписи.ВремяНачала);
			ВыбДатаОкончания = ВыборкаДетальныеЗаписи.Дата -('00010101' - ВыборкаДетальныеЗаписи.ВремяОкончания);
			//НовыйЭлемент = ЭлементыПланировщика.Добавить(ВыбДатаНачала, ВыбДатаОкончания);
			НовыйЭлемент = Планировщик.ИнтервалыФона.Добавить(ВыбДатаНачала, ВыбДатаОкончания);
			//НовыйЭлемент.Текст = НовыйЭлемент.Текст+"Педагог: " +ФильтрПедагог;
			//НовыйЭлемент.Значение = ФильтрПедагог.Ссылка;               		
			//НовыйЭлемент.Картинка = Ур;	
			НовыйЭлемент.Цвет = WebЦвета.ДымчатоБелый;
			//НовыйЭлемент.ЦветФона = WebЦвета.СеребристоСерый;
		КонецЦикла;		
	КонецЕсли;
	
	
	
	Если ОтображатьНапоминания Тогда	
		Запрос = Новый Запрос;
		Запрос.Текст = 
		"ВЫБРАТЬ
		|	НапоминанияПользователя.ВремяСобытия,
		|	НапоминанияПользователя.СрокНапоминания,
		|	НапоминанияПользователя.Описание,
		|	НапоминанияПользователя.ИнтервалВремениНапоминания
		|ИЗ
		|	РегистрСведений.НапоминанияПользователя КАК НапоминанияПользователя";
		
		РезультатЗапроса = Запрос.Выполнить();	
		Напоминания = РезультатЗапроса.Выбрать();
		
		Пока Напоминания.Следующий() Цикл
			Начало  = Напоминания.ВремяСобытия;
			Конец   = Напоминания.ВремяСобытия+Напоминания.ИнтервалВремениНапоминания;
			
			НовыйЭлемент = ЭлементыПланировщика.Добавить(НачалоДня(Начало), КонецДня(Конец));
			НовыйЭлемент.Текст              = Напоминания.Описание;
			НовыйЭлемент.ЦветФона       = WebЦвета.БледноЗолотистый;
			НовыйЭлемент.Картинка = Напом;
			
			СтруктураЗаписи = Новый Структура;
			Для Каждого Измерение Из Метаданные.РегистрыСведений.НапоминанияПользователя.Измерения Цикл
				СтруктураЗаписи.Вставить(Измерение.Имя);
			КонецЦикла;
			ЗаполнитьЗначенияСвойств(СтруктураЗаписи,Напоминания);
			КлючЗаписи = РегистрыСведений.НапоминанияПользователя.СоздатьКлючЗаписи(СтруктураЗаписи);
			НовыйЭлемент.Значение = КлючЗаписи;
			
		КонецЦикла;
	КонецЕсли;
	
КонецПроцедуры

&НаКлиенте
Процедура ПланировщикПередНачаломБыстрогоРедактирования(Элемент, СтандартнаяОбработка)
	
	Если НЕ Элементы.Планировщик.ТолькоПросмотр Тогда
		СтандартнаяОбработка = Ложь;       	
		ПоказатьЗначение(,Элемент.ВыделенныеЭлементы[0].Значение);
	КонецЕсли;
	
КонецПроцедуры

//&НаКлиенте
//Процедура ПланировщикПриАктивизации(Элемент, СтандартнаяОбработка)
	
	//Если НЕ Элементы.Планировщик.ТолькоПросмотр Тогда 
	//	СтандартнаяОбработка = Ложь;
	//	
	//	//Если ТипЗнч(Элемент.ВыделенныеЭлементы[0].Значение) = Тип("ДокументСсылка.Урок") Тогда
	//	Если Элемент.ВыделенныеЭлементы.Количество() > 0 Тогда
	//		ПоказатьЗначение(,Элемент.ВыделенныеЭлементы[0].Значение);
	//	КонецЕсли;
	//КонецЕсли;
	//Пар = Новый Структура("Ключ", Элемент.ВыделенныеЭлементы[0].Значение);
	//ОткрытьФорму("Документ.Урок.Форма.ФормаДокумента", Пар,ЭтотОбъект,,ВариантОткрытияОкна.ОтдельноеОкно,,,РежимОткрытияОкнаФормы.БлокироватьОкноВладельца);				
	//Иначе		
	//Попытка
	//КлючНапоминания = Элементы.Планировщик.ВыделенныеЭлементы[0].Значение;
	//ПараметрыФормы = Новый Структура;
	//ПараметрыФормы.Вставить("Ключ",КлючНапоминания);
	//ОткрытьФорму("РегистрСведений.НапоминанияПользователя.Форма.Напоминание", ПараметрыФормы, ЭтаФорма, УникальныйИдентификатор);
	//ПоказатьЗначение(,Элемент.ВыделенныеЭлементы[0].Значение);
	//Исключение
	//КонецПопытки; 		
	//КонецЕсли;	
	
//КонецПроцедуры

&НаКлиенте
Процедура КалендарьПриАктивизацииДаты(Элемент)
	
	СтарыйМассив = Элементы.Календарь.ВыделенныеДаты;
	СписокЗначений = Новый СписокЗначений;
	СписокЗначений.ЗагрузитьЗначения(СтарыйМассив);
	СписокЗначений.СортироватьПоЗначению();
	НовыйМассив = СписокЗначений.ВыгрузитьЗначения(); 
	
	Если КалендарьПоследняяДата.Количество() = 0 Или КалендарьПоследняяДата[0].Значение <> Календарь Тогда 
		КалендарьПоследняяДата.Вставить(0,Календарь);
	КонецЕсли;
	Пока КалендарьПоследняяДата.Количество() > 2 Цикл
		КалендарьПоследняяДата.Удалить(2);
	КонецЦикла;
	
	НачалоПериода = НовыйМассив[0];
	КонецПериода = КонецДня(НовыйМассив[НовыйМассив.Количество()-1]);
	
	Если Переключатель = "День" Тогда
		ДатаНачала = НачалоДня(НачалоПериода);
		ДатаОкончания = КонецДня(КонецПериода);
	ИначеЕсли Переключатель = "Неделя" Тогда
		ДатаНачала = НачалоНедели(НачалоПериода);
		ДатаОкончания = КонецНедели(КонецПериода);
	ИначеЕсли Переключатель = "Месяц" Тогда
		ДатаНачала = НачалоМесяца(НачалоПериода);
		ДатаОкончания = КонецМесяца(КонецПериода);
	КонецЕсли; 
	
	ЗаполнитьНаСервере(ДатаНачала,ДатаОкончания);
	Элементы.Календарь.Обновить();
	
КонецПроцедуры

&НаСервере
Процедура СформироватьСписокЗанятыхДат();
	
	ТЗЗанятыеДаты.Очистить();
	
	ТЗЗ = Новый ТаблицаЗначений;
	ТЗЗ.Колонки.Добавить("Дата");
	
	Запрос = Новый Запрос;
	Запрос.Текст = 
	"ВЫБРАТЬ
	|	Урок.Дата КАК Дата
	|ИЗ
	|	Документ.LM_Урок КАК Урок
	|ГДЕ
	|	Урок.Проведен = ИСТИНА
	|	И Урок.Дата >= &ДатаНачала
	|	И Урок.Педагог = &Педагог
	|	И Урок.Помещение = &Помещение
	|	И Урок.ГруппаОбучения = &ГруппаОбучения
	|	И Урок.Дата <= &ДатаОкончания";
	
	Запрос.УстановитьПараметр("Педагог", ФильтрПедагог);
	Если НЕ ЗначениеЗаполнено(ФильтрПедагог) Тогда
		Запрос.Текст = СтрЗаменить(Запрос.Текст,"И Урок.Педагог = &Педагог","");
	КонецЕсли;
	
	Запрос.УстановитьПараметр("Помещение", ФильтрПомещение);
	Если НЕ ЗначениеЗаполнено(ФильтрПомещение) Тогда
		Запрос.Текст = СтрЗаменить(Запрос.Текст,"И Урок.Помещение = &Помещение","");
	КонецЕсли;
	
	Запрос.УстановитьПараметр("ГруппаОбучения", ФильтрГруппаОбучения);
	Если НЕ ЗначениеЗаполнено(ФильтрГруппаОбучения) Тогда
		Запрос.Текст = СтрЗаменить(Запрос.Текст,"И Урок.ГруппаОбучения = &ГруппаОбучения","");
	КонецЕсли;
	
	Если Календарь = '00010101' Тогда
		Запрос.УстановитьПараметр("ДатаНачала", НачалоМесяца(НачалоМесяца(ТекущаяДата())-1));
		Запрос.УстановитьПараметр("ДатаОкончания", КонецМесяца(КонецМесяца(ТекущаяДата())+1)); 
	Иначе
		Запрос.УстановитьПараметр("ДатаНачала", НачалоМесяца(НачалоМесяца(Календарь)-1));
		Запрос.УстановитьПараметр("ДатаОкончания", КонецМесяца(КонецМесяца(Календарь)+1)); 
	КонецЕсли;
	РезультатЗапроса = Запрос.Выполнить(); 	
	ВыборкаДетальныеЗаписи = РезультатЗапроса.Выбрать();
	
	Пока ВыборкаДетальныеЗаписи.Следующий() Цикл
		НовСтр = ТЗЗ.Добавить();
		НовСтр.Дата = НачалоДня(ВыборкаДетальныеЗаписи.Дата);
	КонецЦикла; 	 	
	
	ТЗЗ.Свернуть("Дата");
	ТЗЗанятыеДаты.Загрузить(ТЗЗ);
	
КонецПроцедуры


&НаКлиенте
Процедура КалендарьПриВыводеПериода(Элемент, ОформлениеПериода)
	
	Для Каждого ОформлениеДаты Из ОформлениеПериода.Даты Цикл
		
		Отбор = Новый Структура();
		Отбор.Вставить("Дата",ОформлениеДаты.Дата);
		Если ТЗЗанятыеДаты.НайтиСтроки(Отбор).Количество()>0 Тогда //ТЗЗанятыеДаты.НайтиПоЗначению(ОформлениеДаты.Дата) <> Неопределено 
			ОформлениеДаты.ЦветФона = WebЦвета.Бирюзовый;
		КонецЕсли;
		
		//Подсвечиваем текущий день
		//Если НачалоДня(ОформлениеДаты.Дата) = НачалоДня(ТекущаяДата()) Тогда 
		//ОформлениеДаты.ЦветТекста = WebЦвета.Золотистый;
		//ОформлениеДаты.Шрифт = Новый Шрифт(,12,Истина,,Истина);
		//КонецЕсли;
	КонецЦикла;
	
КонецПроцедуры  

&НаКлиенте
Процедура ПриОткрытии(Отказ)
	
	Если Не ЗначениеЗаполнено(ПоложениеШкалыВремениТекст) Тогда
		ПоложениеШкалыВремениТекст = "Лево"; 	
	КонецЕсли;
	
	//Если Переключатель = "День" Тогда 
	//	Элементы.Календарь.НачалоПериодаОтображения = НачалоДня(ТекущаяДата());		
	//	Элементы.Календарь.КонецПериодаОтображения = КонецДня(ТекущаяДата());
	//ИначеЕсли Переключатель = "Неделя" Тогда 
	//	Элементы.Календарь.НачалоПериодаОтображения = НачалоНедели(ТекущаяДата());		
	//	Элементы.Календарь.КонецПериодаОтображения = НачалоНедели(ТекущаяДата());
	//ИначеЕсли Переключатель = "Месяц" Тогда 
	//	Элементы.Календарь.НачалоПериодаОтображения = НачалоМесяца(ТекущаяДата());		
	//	Элементы.Календарь.КонецПериодаОтображения = НачалоМесяца(ТекущаяДата());
	//КонецЕсли; 
	#Если ВебКлиент Тогда
		Элементы.Планировщик.ТолькоПросмотр = Истина;
	#КонецЕсли 	
			
	СформироватьСписокЗанятыхДат();
	ЗаполнитьНаКлиенте(Неопределено, Неопределено);
	
КонецПроцедуры

&НаКлиенте
Процедура ВыбратьПериод(Команда) 
	ЗаполнитьНаКлиенте(Неопределено, Неопределено);
КонецПроцедуры 

&НаКлиенте
Процедура ЗаполнитьНаКлиенте(ДатаНач = Неопределено, ДатаОконч = Неопределено)
	
	СформироватьСписокЗанятыхДат();
	
	Элементы.Календарь.ВыделенныеДаты.Очистить();	
	Если ДатаНач <> Неопределено Тогда 
		ДатаНачала = ДатаНач;
		ДатаОкончания = ДатаОконч;
	ИначеЕсли Календарь = '00010101' Тогда
		ДатаНачала = ТекущаяДата();
		ДатаОкончания = ТекущаяДата();
	Иначе
		ДатаНачала = Календарь;
		ДатаОкончания = Календарь;
		Элементы.Календарь.ВыделенныеДаты.Добавить(Календарь);
	КонецЕсли;
	
	Если Переключатель = "День" Тогда
		ДатаНачала = НачалоДня(ДатаНачала);
		ДатаОкончания = КонецДня(ДатаОкончания);
		Планировщик.ОтображатьТекущуюДату = Ложь;
		Планировщик.ЕдиницаПериодическогоВарианта = ТипЕдиницыШкалыВремени.Час;
		Планировщик.КратностьПериодическогоВарианта = 24;
		Планировщик.ОтступСНачалаПереносаШкалыВремени = 8;
		Планировщик.ОтступСКонцаПереносаШкалыВремени = 0;
		Планировщик.ОтображатьПеренесенныеЗаголовки = Истина;
		Планировщик.ОтображатьПеренесенныеЗаголовкиШкалыВремени = Ложь;
		Планировщик.ОтображениеВремениЭлементов = ОтображениеВремениЭлементовПланировщика.ВремяНачалаИКонца;
		Планировщик.ФорматПеренесенныхЗаголовковШкалыВремени = "ДФ='dddd, d MMMM yyyy'";
		Если ПоложениеШкалыВремениТекст = "Лево" Тогда
			Планировщик.ШкалаВремени.Положение = ПоложениеШкалыВремени.Лево;
		ИначеЕсли ПоложениеШкалыВремениТекст = "Верх" Тогда
			Планировщик.ШкалаВремени.Положение = ПоложениеШкалыВремени.Верх;
		ИначеЕсли ПоложениеШкалыВремениТекст = "Низ" Тогда
			Планировщик.ШкалаВремени.Положение = ПоложениеШкалыВремени.Низ;
		ИначеЕсли ПоложениеШкалыВремениТекст = "Право" Тогда
			Планировщик.ШкалаВремени.Положение = ПоложениеШкалыВремени.Право;
		КонецЕсли; 
		Планировщик.ШкалаВремени.Элементы[0].Формат = "ДФ=ЧЧ:мм";
		Планировщик.ШкалаВремени.Элементы[0].Кратность = 30;
		Планировщик.ШкалаВремени.Элементы[0].Единица = ТипЕдиницыШкалыВремени.Минута;
	ИначеЕсли Переключатель = "Неделя" Тогда
		ДатаНачала = НачалоНедели(ДатаНачала);
		ДатаОкончания = КонецНедели(ДатаОкончания);
		Планировщик.ОтображатьТекущуюДату = Ложь;
		Планировщик.ЕдиницаПериодическогоВарианта = ТипЕдиницыШкалыВремени.Час;
		Планировщик.КратностьПериодическогоВарианта = 24;
		Планировщик.ОтступСНачалаПереносаШкалыВремени = 8;
		Планировщик.ОтступСКонцаПереносаШкалыВремени = 0;
		Планировщик.ОтображатьПеренесенныеЗаголовки = Истина;
		Планировщик.ОтображатьПеренесенныеЗаголовкиШкалыВремени = Ложь;
		Планировщик.ОтображениеВремениЭлементов = ОтображениеВремениЭлементовПланировщика.НеОтображать;
		Планировщик.ФорматПеренесенныхЗаголовковШкалыВремени = "ДФ='ddd, d MMMM'";
		Если ПоложениеШкалыВремениТекст = "Лево" Тогда
			Планировщик.ШкалаВремени.Положение = ПоложениеШкалыВремени.Лево;
		ИначеЕсли ПоложениеШкалыВремениТекст = "Верх" Тогда
			Планировщик.ШкалаВремени.Положение = ПоложениеШкалыВремени.Верх;
		ИначеЕсли ПоложениеШкалыВремениТекст = "Низ" Тогда
			Планировщик.ШкалаВремени.Положение = ПоложениеШкалыВремени.Низ;
		ИначеЕсли ПоложениеШкалыВремениТекст = "Право" Тогда
			Планировщик.ШкалаВремени.Положение = ПоложениеШкалыВремени.Право;
		КонецЕсли; 
		Планировщик.ШкалаВремени.Элементы[0].Формат = "ДФ=ЧЧ:мм";
		Планировщик.ШкалаВремени.Элементы[0].Кратность = 30;
		Планировщик.ШкалаВремени.Элементы[0].Единица = ТипЕдиницыШкалыВремени.Минута;
	ИначеЕсли Переключатель = "Месяц" Тогда
		ДатаНачала = НачалоМесяца(ДатаНачала);
		ДатаОкончания = КонецМесяца(ДатаОкончания);
		
		Планировщик.ОтображатьТекущуюДату = Ложь;
		Планировщик.ЕдиницаПериодическогоВарианта = ТипЕдиницыШкалыВремени.День;
		Планировщик.КратностьПериодическогоВарианта = 7;
		Планировщик.ОтступСНачалаПереносаШкалыВремени = 0;
		Планировщик.ОтступСКонцаПереносаШкалыВремени = 0;
		Планировщик.ОтображатьПеренесенныеЗаголовки = Ложь;
		Планировщик.ОтображатьПеренесенныеЗаголовкиШкалыВремени = Истина;
		Планировщик.ОтображениеВремениЭлементов = ОтображениеВремениЭлементовПланировщика.НеОтображать;
		Планировщик.ФорматПеренесенныхЗаголовковШкалыВремени = "ДФ='ddd, d MMM yyyy'";
		Планировщик.ШкалаВремени.Положение = ПоложениеШкалыВремени.Лево;
		Планировщик.ШкалаВремени.Элементы[0].Формат = "ДФ='ddd, d MMM yyyy'";
		Планировщик.ШкалаВремени.Элементы[0].Кратность = 1;
		Планировщик.ШкалаВремени.Элементы[0].Единица = ТипЕдиницыШкалыВремени.День;
		
		Интервал = Планировщик.ИнтервалыФона.Добавить(НачалоМесяца(ДатаНачала), КонецМесяца(ДатаОкончания));
		Интервал.Цвет = Новый Цвет(250, 250, 250);
		//Если НастройкиОтображения.ОтображатьТекущуюДату Тогда
		//	ТекущаяДатаСеанса = ТекущаяДатаСеанса();
		//	Интервал = Планировщик.ИнтервалыФона.Добавить(НачалоДня(ТекущаяДатаСеанса), КонецДня(ТекущаяДатаСеанса));
		//	Интервал.Цвет = Новый Цвет(223, 255, 223);
		//КонецЕсли; 
		
	КонецЕсли;   
	
	ЗаполнитьНаСервере(ДатаНачала,ДатаОкончания);
	
	Элементы.Календарь.Обновить();
	
КонецПроцедуры

&НаКлиенте
Процедура ПланировщикПередСозданием(Элемент, Начало, Конец, Значения, Текст, СтандартнаяОбработка)
	
	Если НЕ Элементы.Планировщик.ТолькоПросмотр Тогда
		СтандартнаяОбработка = Ложь;
		
		//ПараметрыФормы = Новый Структура;
		//ПараметрыФормы.Вставить("Дата",Начало);
		//ОткрытьФорму("РегистрСведений.НапоминанияПользователя.Форма.Напоминание", ПараметрыФормы, ЭтаФорма, УникальныйИдентификатор);
		Форма = ПолучитьФорму("Документ.LM_Урок.Форма.ФормаДокумента");
		Форма.Объект.Дата = Начало;
		Форма.Открыть();
		//ОткрытьФорму("Документ.Урок.Форма.ФормаДокумента", ПараметрыФормы, ЭтаФорма, УникальныйИдентификатор);
	КонецЕсли;
	
КонецПроцедуры

&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
	
	Планировщик.ФорматПеренесенныхЗаголовковШкалыВремени = "ДФ='dd MMMM yyy (дддд)'";
	Переключатель = "Неделя";
	Цвет		  = "ПредмОбуч";
	
	Если НЕ РольДоступна("ПолныеПрава") Тогда 
		Элементы.Планировщик.ТолькоПросмотр = Истина;
		Элементы.Google_синхронизация.Доступность = Ложь;
	КонецЕсли;  
	     	
КонецПроцедуры

&НаКлиенте
Процедура ПереключательПриИзменении(Элемент)
	ЗаполнитьНаКлиенте(Планировщик.ТекущиеПериодыОтображения[0].Начало, Планировщик.ТекущиеПериодыОтображения[0].Конец);
КонецПроцедуры

&НаКлиенте
Процедура ПланировщикПриСменеТекущегоПериодаОтображения(Элемент, ТекущиеПериодыОтображения, СтандартнаяОбработка)
	
	СтандартнаяОбработка = Ложь;
	
	НачалоПериода = ТекущиеПериодыОтображения[0].Начало;
	КонецПериода = ТекущиеПериодыОтображения[0].Начало;//ТекущиеПериодыОтображения[0].Конец;
	
	Если Переключатель = "День" Тогда
		ДатаНачала = НачалоДня(ТекущиеПериодыОтображения[0].Начало);
		ДатаОкончания = КонецДня(ТекущиеПериодыОтображения[0].Начало);
	ИначеЕсли Переключатель = "Неделя" Тогда
		ДатаНачала = НачалоНедели(ТекущиеПериодыОтображения[0].Начало);
		ДатаОкончания = КонецНедели(ТекущиеПериодыОтображения[0].Начало);
	ИначеЕсли Переключатель = "Месяц" Тогда
		ДатаНачала = НачалоМесяца(НачалоПериода);
		ДатаОкончания = КонецМесяца(КонецПериода);
	КонецЕсли; 
	
	ЗаполнитьНаСервере(ДатаНачала,ДатаОкончания);
	Элементы.Календарь.Обновить();
	
КонецПроцедуры

&НаКлиенте
Процедура ПланировщикПеретаскивание(Элемент, ПараметрыПеретаскивания, СтандартнаяОбработка, Дата, Значения)
	СтандартнаяОбработка = Ложь;
КонецПроцедуры

&НаКлиенте
Процедура ПланировщикВыбор(Элемент, СтандартнаяОбработка)
	Если НЕ Элементы.Планировщик.ТолькоПросмотр Тогда
		СтандартнаяОбработка = Ложь;
		ПоказатьЗначение(,Элемент.ВыделенныеЭлементы[0].Значение);
	КонецЕсли;
КонецПроцедуры

&НаКлиенте
Процедура Google_синхронизация(Команда)
	ОткрытьФорму("Обработка.LM_Календарь.Форма.ФормаGoogle", , ЭтаФорма);
КонецПроцедуры

&НаКлиенте
Процедура Обновить(Команда)
	ЗаполнитьНаКлиенте(Планировщик.ТекущиеПериодыОтображения[0].Начало, Планировщик.ТекущиеПериодыОтображения[0].Конец);
КонецПроцедуры

&НаКлиенте
Процедура Цвет1ПриИзменении(Элемент)
	ЗаполнитьНаКлиенте(Планировщик.ТекущиеПериодыОтображения[0].Начало, Планировщик.ТекущиеПериодыОтображения[0].Конец);
КонецПроцедуры




////////////////Управление периодами планировщика//////////////////////////////////
&НаКлиенте
Процедура ПредыдущийПериод(Команда)
	
	НачалоПериода = НачалоДня(Планировщик.ТекущиеПериодыОтображения[0].Начало);
	//КонецПериода = ТекущиеПериодыОтображения[0].Начало;
	
	Если Переключатель = "День" Тогда
		ДатаНачала = НачалоДня(НачалоПериода-1);
		ДатаОкончания = КонецДня(НачалоПериода-1);
	ИначеЕсли Переключатель = "Неделя" Тогда
		ДатаНачала = НачалоНедели(НачалоПериода-1);
		ДатаОкончания = КонецНедели(НачалоПериода-1);
	ИначеЕсли Переключатель = "Месяц" Тогда
		ДатаНачала = НачалоМесяца(НачалоПериода-1);
		ДатаОкончания = КонецМесяца(НачалоПериода-1);
	КонецЕсли; 
	
	ЗаполнитьНаСервере(ДатаНачала,ДатаОкончания);
	Элементы.Календарь.Обновить();	
	
КонецПроцедуры

&НаКлиенте
Процедура БудущийПериод(Команда)
	
	НачалоПериода = КонецДня(Планировщик.ТекущиеПериодыОтображения[0].Конец);
	
	Если Переключатель = "День" Тогда
		ДатаНачала = НачалоДня(НачалоПериода+1);
		ДатаОкончания = КонецДня(НачалоПериода+1);
	ИначеЕсли Переключатель = "Неделя" Тогда
		ДатаНачала = НачалоНедели(НачалоПериода+1);
		ДатаОкончания = КонецНедели(НачалоПериода+1);
	ИначеЕсли Переключатель = "Месяц" Тогда
		ДатаНачала = НачалоМесяца(НачалоПериода+1);
		ДатаОкончания = КонецМесяца(НачалоПериода+1);
	КонецЕсли; 
	
	ЗаполнитьНаСервере(ДатаНачала,ДатаОкончания);
	Элементы.Календарь.Обновить();		
	
КонецПроцедуры

&НаКлиенте
Процедура Сегодня(Команда)
	
	НачалоПериода = НачалоДня(ТекущаяДата());
	
	Если Переключатель = "День" Тогда
		ДатаНачала = НачалоДня(НачалоПериода);
		ДатаОкончания = КонецДня(НачалоПериода);
	ИначеЕсли Переключатель = "Неделя" Тогда
		ДатаНачала = НачалоНедели(НачалоПериода);
		ДатаОкончания = КонецНедели(НачалоПериода);
	ИначеЕсли Переключатель = "Месяц" Тогда
		ДатаНачала = НачалоМесяца(НачалоПериода);
		ДатаОкончания = КонецМесяца(НачалоПериода);
	КонецЕсли; 
	
	ЗаполнитьНаСервере(ДатаНачала,ДатаОкончания);
	Элементы.Календарь.Обновить();
	
КонецПроцедуры

&НаКлиенте
Процедура КалендарьПриИзменении(Элемент)
	СформироватьСписокЗанятыхДат();
КонецПроцедуры
