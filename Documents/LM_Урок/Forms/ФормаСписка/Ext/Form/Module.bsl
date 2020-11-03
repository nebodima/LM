﻿&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
	
	Если ОтображатьДиаграммуЗадолженности Тогда
		ПостроитьДиаграмму();
	КонецЕсли;
	
	Если ОтображатьБлижайшиеДниРождения Тогда
		СформироватьСписокДнейРождений();
	КонецЕсли;
	
	//Ф = ПолучитьТекущийСеансИнформационнойБазы().ИмяПриложения;
	//СеансыИБ = ПолучитьСеансыИнформационнойБазы();        
	//Для Каждого Сеанс Из СеансыИБ Цикл         
	//	Если Сеанс.НомерСоединения = ПолучитьТекущийСеансИнформационнойБазы().НомерСоединения Тогда
	//		//ИмяПриложения = Сеанс.ИмяПриложения;
	//		ВидКлиента = Сеанс.ИмяПриложения;//Строка(ПредставлениеПриложения(Сеанс.ИмяПриложения));
	//	КонецЕсли;   
	//КонецЦикла;
	//
	//Сообщить(ВидКлиента);
	//
	//ВидКлиента = "";
	//#Если ВебКлиент Тогда
	//	ВидКлиента = "ВебКлиент";
	//#ИначеЕсли Клиент Тогда
	//	ВидКлиента = "Клиент";		
	//#ИначеЕсли ВнешнееСоединение Тогда
	//	ВидКлиента = "ВнешнееСоединение";		
	//#ИначеЕсли ТонкийКлиент Тогда
	//	ВидКлиента = "ТонкийКлиент";		
	//#ИначеЕсли МобильныйКлиент Тогда
	//	ВидКлиента = "МобильныйКлиент";
	//#Иначе
	//	ВидКлиента = "Неопределен";
	//#КонецЕсли
	//
	//Если ВидКлиента = "MobileClient" Тогда
	//	Элементы.ГруппаНастройка.Видимость = Ложь;
	//	//ОтображатьБлижайшиеДниРождения = Ложь;
	//	//ОтображатьДиаграммуЗадолженности = Ложь;
	//КонецЕсли	
	
КонецПроцедуры

&НаКлиенте
Процедура РасшифровкаВыбор(Элемент, ВыбраннаяСтрока, Поле, СтандартнаяОбработка)
	
	Если Поле.Имя = "РасшифровкаУченик" Тогда
		Значение = Элементы.Расшифровка.ТекущиеДанные.Ученик;
		ПоказатьЗначение(,Значение);
	ИначеЕсли Поле.Имя = "РасшифровкаАбонемент" Тогда
		Значение = Элементы.Расшифровка.ТекущиеДанные.Абонемент;
		ПоказатьЗначение(,Значение);                        
	ИначеЕсли Поле.Имя = "РасшифровкаСуммаОстаток" Тогда
		ПараметрыОткрытия = ОткрытьВзаиморасчетыНаСервере(Элементы.Расшифровка.ТекущиеДанные.Ученик);
		ОткрытьФорму("Отчет.LM_Взаиморасчеты.Форма", ПараметрыОткрытия, ЭтаФорма);
	ИначеЕсли Поле.Имя = "РасшифровкаСуммаОстатокПоПредмету" Тогда
		ПараметрыОткрытия = ОткрытьВзаиморасчетыНаСервере(Элементы.Расшифровка.ТекущиеДанные.Ученик);
		ОткрытьФорму("Отчет.LM_Взаиморасчеты.Форма", ПараметрыОткрытия, ЭтаФорма);		
	Иначе
		ПоказатьЗначение(,Элементы.Список.ТекущаяСтрока);		
	КонецЕсли;
	
КонецПроцедуры

&НаКлиенте
Процедура СписокПриАктивизацииСтроки(Элемент)
	
	Если НеОтображатьДетализациюУрока = Ложь Тогда 		
		Если ТипЗнч(Элементы.Список.ТекущаяСтрока) = Тип("СтрокаГруппировкиДинамическогоСписка") Тогда
			
			Расшифровка.Отбор.Элементы.Очистить();
			ЭлементОтбора = Расшифровка.Отбор.Элементы.Добавить(Тип("ЭлементОтбораКомпоновкиДанных"));
			ЭлементОтбора.ЛевоеЗначение = Новый ПолеКомпоновкиДанных("Ссылка");
			ЭлементОтбора.ВидСравнения = ВидСравненияКомпоновкиДанных.Равно;
			ЭлементОтбора.ПравоеЗначение = Неопределено;
			ЭлементОтбора = Расшифровка.Отбор.Элементы[0];
			ЭлементОтбора.Использование = Истина;
			Элементы.Расшифровка.Обновить();
			
		Иначе
						
			Урок = Элементы.Список.ТекущаяСтрока;
			Расшифровка.Отбор.Элементы.Очистить();
			ЭлементОтбора = Расшифровка.Отбор.Элементы.Добавить(Тип("ЭлементОтбораКомпоновкиДанных"));
			ЭлементОтбора.ЛевоеЗначение = Новый ПолеКомпоновкиДанных("Ссылка");
			ЭлементОтбора.ВидСравнения = ВидСравненияКомпоновкиДанных.Равно;
			ЭлементОтбора.ПравоеЗначение = Урок;
			ЭлементОтбора = Расшифровка.Отбор.Элементы[0];
			ЭлементОтбора.Использование = Истина;
			Элементы.Расшифровка.Обновить();
			
			//Расшифровка.Параметры.УстановитьЗначениеПараметра("Ссылка",Элементы.Список.ТекущаяСтрока);

		КонецЕсли; 		
	КонецЕсли;
	
КонецПроцедуры 

&НаКлиенте
Процедура ПомощникСозданияУроков(Команда)
	ОткрытьФорму("Документ.LM_Урок.Форма.ПомощникСозданияУроков",,,,); 
КонецПроцедуры

&НаКлиенте
Процедура УченикПриИзменении(Элемент)
	Абонемент = Неопределено;
	УченикПриИзмененииНаСервере();
КонецПроцедуры

&НаКлиенте
Процедура АбонементПриИзменении(Элемент)
	Ученик = Неопределено;
	АбонементПриИзмененииНаСервере();
КонецПроцедуры

Процедура АбонементПриИзмененииНаСервере()
	
	Список.Отбор.Элементы.Очистить();
	
	Если ЗначениеЗаполнено(Абонемент) Тогда
		ЭлементОтбора = Список.Отбор.Элементы.Добавить(Тип("ЭлементОтбораКомпоновкиДанных"));
		ЭлементОтбора.ЛевоеЗначение = Новый ПолеКомпоновкиДанных("Ученики.Абонемент");
		ЭлементОтбора.ВидСравнения = ВидСравненияКомпоновкиДанных.Равно;
		ЭлементОтбора.ПравоеЗначение = Абонемент;
		ЭлементОтбора = Список.Отбор.Элементы[0];
		ЭлементОтбора.Использование = Истина;
		Элементы.Список.Обновить();		
	Иначе		
		Элементы.Список.Обновить();		
	КонецЕсли;   
	
КонецПроцедуры

Процедура УченикПриИзмененииНаСервере()
	
	Список.Отбор.Элементы.Очистить();
	
	Если ЗначениеЗаполнено(Ученик) Тогда
		ЭлементОтбора = Список.Отбор.Элементы.Добавить(Тип("ЭлементОтбораКомпоновкиДанных"));
		ЭлементОтбора.ЛевоеЗначение = Новый ПолеКомпоновкиДанных("Ученики.Ученик");
		ЭлементОтбора.ВидСравнения = ВидСравненияКомпоновкиДанных.Равно;
		ЭлементОтбора.ПравоеЗначение = Ученик;
		ЭлементОтбора = Список.Отбор.Элементы[0];
		ЭлементОтбора.Использование = Истина;
		Элементы.Список.Обновить();		
	Иначе		
		Элементы.Список.Обновить();		
	КонецЕсли;   
	
КонецПроцедуры

Процедура ПостроитьДиаграмму()
	
	Диаграмма.Очистить();
	
	Запрос = Новый Запрос;
	Запрос.Текст = 
	"ВЫБРАТЬ
	|	СписанияСуммЗаУроки.Клиент КАК Клиент,
	|	-СписанияСуммЗаУроки.СуммаОстаток КАК СуммаОстаток
	|ИЗ
	|	РегистрНакопления.LM_СписанияСуммЗаУроки.Остатки(, ) КАК СписанияСуммЗаУроки
	|ГДЕ
	|	НЕ СписанияСуммЗаУроки.Клиент.ЭтоПедагог
	|
	|УПОРЯДОЧИТЬ ПО
	|	СуммаОстаток УБЫВ
	|АВТОУПОРЯДОЧИВАНИЕ";
	
	ТЗ = Запрос.Выполнить().Выгрузить(); 	
	
	Точка = Диаграмма.Точки.Добавить("");
	
	Для Каждого СтрТЗ из ТЗ Цикл
		
		Серия = Диаграмма.Серии.Добавить();
		Серия.Значение 		= СтрТЗ.Клиент;
		Серия.Текст 		= "" +СтрТЗ.Клиент+ " " +Формат(СтрТЗ.СуммаОстаток,"ЧДЦ=2; ЧФ=(Ч)");
		Серия.Расшифровка 	= СтрТЗ.Клиент; 
		
		Диаграмма.УстановитьЗначение(Точка,Серия,СтрТЗ.СуммаОстаток,СтрТЗ.Клиент);
		
	КонецЦикла;
	
КонецПроцедуры

&НаКлиенте
Процедура ОбработкаОповещения(ИмяСобытия, Параметр, Источник)
	
	Если ИмяСобытия = "ЗакрытьФормуНастройкиСписка" Тогда
		//ЗаполнитьЗначенияСвойств(ЭтотОбъект,Параметр);
		//ОбновитьФормуНаКлиенте();
	ИначеЕсли ИмяСобытия = "ЗакрытьФормуУрока" Тогда
		Урок = Элементы.Список.ТекущаяСтрока;
		Расшифровка.Отбор.Элементы.Очистить();
		ЭлементОтбора = Расшифровка.Отбор.Элементы.Добавить(Тип("ЭлементОтбораКомпоновкиДанных"));
		ЭлементОтбора.ЛевоеЗначение = Новый ПолеКомпоновкиДанных("Ссылка");
		ЭлементОтбора.ВидСравнения = ВидСравненияКомпоновкиДанных.Равно;
		ЭлементОтбора.ПравоеЗначение = Урок;
		ЭлементОтбора = Расшифровка.Отбор.Элементы[0];
		ЭлементОтбора.Использование = Истина;
		Элементы.Расшифровка.Обновить();
	КонецЕсли;	
	
КонецПроцедуры

&НаКлиенте
Процедура ОбновитьФормуНаКлиенте()
	
	Если ОтображатьБлижайшиеДниРождения Тогда
		СформироватьСписокДнейРождений();
		Элементы.ГруппаДниРождения.Видимость = Истина;
	Иначе
		Элементы.ГруппаДниРождения.Видимость = Ложь;
	КонецЕсли;
	
	Если ОтображатьДиаграммуЗадолженности Тогда
		ПостроитьДиаграмму();
		Элементы.ГруппаДолжники.Видимость = Истина;
	Иначе
		Элементы.ГруппаДолжники.Видимость = Ложь;
	КонецЕсли;
	
	Если НеОтображатьДетализациюУрока Тогда
		Элементы.Расшифровка.Видимость = Ложь;
	Иначе
		Элементы.Расшифровка.Видимость = Истина;
	КонецЕсли;
	
КонецПроцедуры

&НаСервере
Функция ОткрытьВзаиморасчетыНаСервере(Значение)
	
	КомпоновщикНастроек = Отчеты.LM_Взаиморасчеты.Создать().КомпоновщикНастроек; 
	Настройки 			= КомпоновщикНастроек.Настройки; 
	
	ЭлементНастройки = Настройки.ПараметрыДанных.НайтиЗначениеПараметра(Новый ПараметрКомпоновкиДанных("Период")); 
	//ЭлементНастройки.Значение.ДатаНачала    = '00010101';//НачалоГода(ТекущаяДата());
	//ЭлементНастройки.Значение.ДатаОкончания = '00010101';//КонецГода(ТекущаяДата());
	Если ЗначениеЗаполнено(ЭлементНастройки.ИдентификаторПользовательскойНастройки) Тогда 
		ПользовательскийПараметр = КомпоновщикНастроек.ПользовательскиеНастройки.Элементы.Найти(ЭлементНастройки.ИдентификаторПользовательскойНастройки); 
		Если ТипЗнч(ПользовательскийПараметр) = Тип("ЗначениеПараметраНастроекКомпоновкиДанных") Тогда 
			//ПользовательскийПараметр.Значение = ЭлементНастройки.Значение;
			ПользовательскийПараметр.Использование = Ложь;
		КонецЕсли; 
	КонецЕсли; 
	
	ОтборУченик = Новый ПолеКомпоновкиДанных("Клиент");
	//ОтборПериод = Новый ПолеКомпоновкиДанных("Период");
	
	Для Каждого ЭлементНастройки Из Настройки.Отбор.Элементы Цикл 
		Если ЭлементНастройки.ЛевоеЗначение = ОтборУченик Тогда 
			ЭлементНастройки.ВидСравнения = ВидСравненияКомпоновкиДанных.Равно; 
			ЭлементНастройки.ПравоеЗначение = Значение; 
			ЭлементНастройки.Использование = Истина; 
			Если ЗначениеЗаполнено(ЭлементНастройки.ИдентификаторПользовательскойНастройки) Тогда 
				ПользовательскийПараметр = КомпоновщикНастроек.ПользовательскиеНастройки.Элементы.Найти(ЭлементНастройки.ИдентификаторПользовательскойНастройки); 
				Если ТипЗнч(ПользовательскийПараметр) = Тип("ЭлементОтбораКомпоновкиДанных") Тогда 
					ПользовательскийПараметр.ВидСравнения = ЭлементНастройки.ВидСравнения; 
					ПользовательскийПараметр.ПравоеЗначение = ЭлементНастройки.ПравоеЗначение; 
					ПользовательскийПараметр.Использование = ЭлементНастройки.Использование; 
				КонецЕсли; 
			КонецЕсли;
			Прервать; 
		КонецЕсли; 
	КонецЦикла; 
	
	ПараметрыОткрытия = Новый Структура(); 
	ПараметрыОткрытия.Вставить("СформироватьПриОткрытии", Истина); 
	ПараметрыОткрытия.Вставить("Вариант", Настройки); 
	ПараметрыОткрытия.Вставить("ПользовательскиеНастройки", КомпоновщикНастроек.ПользовательскиеНастройки); 
	
	Возврат ПараметрыОткрытия;
	
КонецФункции

&НаКлиенте
Процедура ОткрытьВзаиморасчеты(Команда)
	
	Если ЗначениеЗаполнено(Ученик) Тогда		
		ПараметрыОткрытия = ОткрытьВзаиморасчетыНаСервере(Ученик);
		ОткрытьФорму("Отчет.LM_Взаиморасчеты.Форма", ПараметрыОткрытия, ЭтаФорма);
	Иначе
		ОткрытьФорму("Отчет.LM_Взаиморасчеты.Форма", , ЭтаФорма);
	КонецЕсли;
	
КонецПроцедуры

&НаКлиенте
Процедура ОткрытьВзаиморасчетыКонтекст(Команда)
	
	ПараметрыОткрытия = ОткрытьВзаиморасчетыНаСервере(Элементы.Расшифровка.ТекущиеДанные.Ученик);
	ОткрытьФорму("Отчет.LM_Взаиморасчеты.Форма", ПараметрыОткрытия, ЭтаФорма);
	
КонецПроцедуры

&НаКлиенте
Процедура ОткрытьПанельУченика(Команда)
	
	ОткрытьФорму("Обработка.LM_ПанельУченика.Форма.Форма", , ЭтаФорма);
	
КонецПроцедуры

Процедура СформироватьСписокДнейРождений()
	
	Запрос = Новый Запрос;
	Запрос.Текст = 
	"ВЫБРАТЬ
	|	ФизЛица.Ссылка КАК ФизЛицо,
	|	ФизЛица.ДатаРождения КАК Дата,
	|	ДЕНЬГОДА(ФизЛица.ДатаРождения) КАК ДеньГода,
	|	ДЕНЬГОДА(ФизЛица.ДатаРождения) - &ДеньГода + 1 КАК ОсталосьДней,
	|	ФизЛица.Возраст КАК Возраст
	|ИЗ
	|	Справочник.LM_ФизЛица КАК ФизЛица
	|ГДЕ
	|	ФизЛица.ПометкаУдаления = ЛОЖЬ
	|	И ФизЛица.ЭтоГруппа = ЛОЖЬ
	|	И ФизЛица.ДатаРождения <> ДАТАВРЕМЯ(1, 1, 1, 0, 0, 0)
	|	И ДЕНЬГОДА(ФизЛица.ДатаРождения) - &ДеньГода + 1 < 11
	|	И ДЕНЬГОДА(ФизЛица.ДатаРождения) - &ДеньГода + 1 >= 0
	|";
	
	Запрос.УстановитьПараметр("ДеньГода", ДеньГода(ТекущаяДата()));
	РезультатЗапроса = Запрос.Выполнить().Выгрузить();
	
	ДниРождения.Загрузить(РезультатЗапроса);
	ДниРождения.Сортировать("ОсталосьДней Убыв");
	
КонецПроцедуры

&НаКлиенте
Процедура ПриОткрытии(Отказ)
	
	ВидКлиента = "";
	//#Если ВебКлиент Тогда
	//	ВидКлиента = "ВебКлиент";
	//#ИначеЕсли Клиент Тогда
	//	ВидКлиента = "Клиент";		
	//#ИначеЕсли ВнешнееСоединение Тогда
	//	ВидКлиента = "ВнешнееСоединение";		
	//#ИначеЕсли ТонкийКлиент Тогда
	//	ВидКлиента = "ТонкийКлиент";		
	#Если МобильныйКлиент Тогда
		ВидКлиента = "МобильныйКлиент";
	//#Иначе
	//	ВидКлиента = "Неопределен";
	#КонецЕсли
	
	//Сообщить(ВидКлиента+ " " +ВидКлиента2);
	
	Если ВидКлиента = "МобильныйКлиент" Тогда
		Элементы.ГруппаНастройка.Видимость = Ложь;
		//ОтображатьБлижайшиеДниРождения = Ложь;
		//ОтображатьДиаграммуЗадолженности = Ложь;
	КонецЕсли;	
	
	ОбновитьФормуНаКлиенте();
	
КонецПроцедуры

&НаКлиенте
Процедура ПриИзмененийНайстроек(Элемент)
	ОбновитьФормуНаКлиенте();
КонецПроцедуры

&НаКлиенте
Процедура СписокВыбор(Элемент, ВыбраннаяСтрока, Поле, СтандартнаяОбработка)
	
	СтандартнаяОбработка = Ложь;
	
	Если Поле.Имя = "Педагог" Тогда
		Значение = Элементы.Список.ТекущиеДанные.Педагог;
		ПоказатьЗначение(,Значение);
	Иначе
		ПоказатьЗначение(,Элементы.Список.ТекущаяСтрока);		
	КонецЕсли;
	
КонецПроцедуры

