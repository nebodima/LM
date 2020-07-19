﻿///////////////////////////////////////////////////////////////////////////////////
// Подсистема "Пользователи в модели сервиса".
// 
///////////////////////////////////////////////////////////////////////////////////

#Область ПрограммныйИнтерфейс

// Только для внутреннего использования.
Процедура ОбновитьОписаниеWebСервисаМенеджераСервиса() Экспорт
	
	Если НЕ ОбщегоНазначенияПовтИсп.РазделениеВключено() Тогда
		Возврат;
	КонецЕсли;
	
	УстановитьПривилегированныйРежим(Истина);
	// Кэш должен быть заполнен до записи пользователя ИБ.
	РаботаВМоделиСервиса.ПолучитьПроксиМенеджераСервиса();
	УстановитьПривилегированныйРежим(Ложь);
	
КонецПроцедуры

// Только для внутреннего использования.
Функция ЕстьПравоДобавленияПользователей() Экспорт
	
	УстановитьПривилегированныйРежим(Истина);
	Прокси = РаботаВМоделиСервиса.ПолучитьПроксиМенеджераСервиса();
	УстановитьПривилегированныйРежим(Ложь);
	
	ОбластьДанных = Прокси.ФабрикаXDTO.Создать(
		Прокси.ФабрикаXDTO.Тип("http://www.1c.ru/SaaS/ApplicationAccess", "Zone"));
	ОбластьДанных.Zone = РаботаВМоделиСервиса.ЗначениеРазделителяСеанса();
	
	ИнформацияОбОшибке = Неопределено;
	ПраваДоступаXDTO = Прокси.GetAccessRights(ОбластьДанных, 
		ИдентификаторСервисаТекущегоПользователя(), ИнформацияОбОшибке);
	ОбработатьИнформациюОбОшибкеWebСервиса(ИнформацияОбОшибке, "GetAccessRights"); // Имя операции не локализуется.
	
	Для каждого ЭлементСпискаПрав Из ПраваДоступаXDTO.Item Цикл
		Если ЭлементСпискаПрав.AccessRight = "CreateUser" Тогда
			Возврат Истина;
		КонецЕсли;
	КонецЦикла;
	
	Возврат Ложь;
	
КонецФункции

// Только для внутреннего использования.
Функция ДействияСНовымПользователемСервиса() Экспорт
	
	ДействияСПользователемСервиса = НовыеДействияСПользователемСервиса();
	ДействияСПользователемСервиса.ИзменениеПароля = Истина;
	ДействияСПользователемСервиса.ИзменениеИмени = Истина;
	ДействияСПользователемСервиса.ИзменениеПолногоИмени = Истина;
	ДействияСПользователемСервиса.ИзменениеДоступа = Истина;
	ДействияСПользователемСервиса.ИзменениеАдминистративногоДоступа = Истина;
	
	ДействияСКИ = ДействияСПользователемСервиса.КонтактнаяИнформация; 
	Для каждого КлючИЗначение Из РаботаВМоделиСервисаПовтИсп.СоответствиеВидовКИПользователяXDTO() Цикл
		ДействияСКИ[КлючИЗначение.Ключ].Изменение = Истина;
	КонецЦикла;
	
	Возврат ДействияСПользователемСервиса;
	
КонецФункции

// Только для внутреннего использования.
Функция ДействияССуществующимПользователемСервиса(Знач Пользователь) Экспорт
	
	УстановитьПривилегированныйРежим(Истина);
	Прокси = РаботаВМоделиСервиса.ПолучитьПроксиМенеджераСервиса();
	УстановитьПривилегированныйРежим(Ложь);
	
	ОбъектыДоступа = ПодготовитьОбъектыДоступаПользователя(Прокси.ФабрикаXDTO, Пользователь);
	
	ИнформацияОбОшибке = Неопределено;
	ПраваДоступаОбъектовXDTO = Прокси.GetObjectsAccessRights(ОбъектыДоступа, 
		ИдентификаторСервисаТекущегоПользователя(), ИнформацияОбОшибке);
	ОбработатьИнформациюОбОшибкеWebСервиса(ИнформацияОбОшибке, "GetObjectsAccessRights"); // Имя операции не локализуется.
	
	Возврат ПраваДоступаОбъектовXDTOВДействияСПользователемСервиса(Прокси.ФабрикаXDTO, ПраваДоступаОбъектовXDTO);
	
КонецФункции

// Только для внутреннего использования.
Функция ДействияСПользователемСервисаПриНедоступностиНастройкиПользователей() Экспорт
	
	ДействияСПользователемСервиса = НовыеДействияСПользователемСервиса();
	ДействияСПользователемСервиса.ИзменениеПароля = Ложь;
	ДействияСПользователемСервиса.ИзменениеИмени = Ложь;
	ДействияСПользователемСервиса.ИзменениеПолногоИмени = Ложь;
	ДействияСПользователемСервиса.ИзменениеДоступа = Ложь;
	ДействияСПользователемСервиса.ИзменениеАдминистративногоДоступа = Ложь;
	
	ДействияСКИ = ДействияСПользователемСервиса.КонтактнаяИнформация;
	Для каждого КлючИЗначение Из РаботаВМоделиСервисаПовтИсп.СоответствиеВидовКИПользователяXDTO() Цикл
		ДействияСКИ[КлючИЗначение.Ключ].Изменение = Ложь;
	КонецЦикла;
	
	Возврат ДействияСПользователемСервиса;
	
КонецФункции

#КонецОбласти

#Область СлужебныйПрограммныйИнтерфейс

// Возвращает флаг доступности действий изменения пользователей.
//
// Возвращаемое значение:
// Булево - Истина, если изменение пользователей доступно, иначе Ложь.
//
Функция ДоступноИзменениеПользователей() Экспорт
	
	Возврат Константы.РежимИспользованияИнформационнойБазы.Получить() 
		<> Перечисления.РежимыИспользованияИнформационнойБазы.Демонстрационный;
	
КонецФункции

// Возвращает доступные текущему пользователю действия с указанным
// пользователем сервиса.
//
// Параметры:
//  Пользователь - СправочникСсылка.Пользователи - пользователь, доступные
//   действия с которым требуется получить. Если не указано, проверяются
//   доступные действия с текущим пользователем.
//  ПарольПользователяСервиса - Строка - пароль текущего пользователя для
//   доступа в сервис.
//  
Функция ПолучитьДействияСПользователемСервиса(Знач Пользователь = Неопределено) Экспорт
	
	Если Пользователь = Неопределено Тогда
		Пользователь = Пользователи.ТекущийПользователь();
	КонецЕсли;
	
	Если ДоступноИзменениеПользователей() Тогда
		
		Если ПользователиИнформационнойБазы.ТекущийПользователь().РазделениеДанных.Количество() = 0 Тогда
			
			Если Пользователи.ЭтоПолноправныйПользователь(, Истина) Тогда
				
				Возврат ДействияСНовымПользователемСервиса();
				
			Иначе
			
				Возврат ДействияСПользователемСервисаПриНедоступностиНастройкиПользователей();
				
			КонецЕсли;
			
		ИначеЕсли ЭтоСуществующийПользовательТекущейОбластиДанных(Пользователь) Тогда
			
			Возврат ДействияССуществующимПользователемСервиса(Пользователь);
			
		Иначе
			
			Если ЕстьПравоДобавленияПользователей() Тогда
				Возврат ДействияСНовымПользователемСервиса();
			Иначе
				ВызватьИсключение НСтр("ru = 'Недостаточно прав доступа для добавления новых пользователей'");
			КонецЕсли;
			
		КонецЕсли;
		
	Иначе
		
		Возврат ДействияСПользователемСервисаПриНедоступностиНастройкиПользователей();
		
	КонецЕсли;
	
КонецФункции

// Формирует запрос на изменение адреса электронной почты пользователя
// сервиса.
//
// Параметры:
//  НоваяПочта - Строка - новый адрес электронной почты пользователя.
//  Пользователь - СправочникСсылка.Пользователи - пользователь, которому
//   требуется изменить адрес электронной почты.
//  ПарольПользователяСервиса - Строка - пароль текущего пользователя
//   для доступа к менеджеру сервиса.
//
Процедура СоздатьЗапросНаСменуПочты(Знач НоваяПочта, Знач Пользователь, Знач ПарольПользователяСервиса) Экспорт
	
	УстановитьПривилегированныйРежим(Истина);
	Прокси = РаботаВМоделиСервиса.ПолучитьПроксиМенеджераСервиса(ПарольПользователяСервиса);
	УстановитьПривилегированныйРежим(Ложь);
	
	ИнформацияОбОшибке = Неопределено;
	Прокси.RequestEmailChange(
		ОбщегоНазначения.ЗначениеРеквизитаОбъекта(Пользователь, "ИдентификаторПользователяСервиса"), 
		НоваяПочта, 
		ИнформацияОбОшибке);
	ОбработатьИнформациюОбОшибкеWebСервиса(ИнформацияОбОшибке, "RequestEmailChange"); // Имя операции не локализуется.
	
КонецПроцедуры

// Создает / обновляет запись пользователя сервиса.
// 
// Параметры:
//  Пользователь - СправочникСсылка.Пользователи/СправочникОбъект.Пользователи
//  СоздатьПользователяСервиса - Булево - Истина - создать нового пользователя
//   сервиса, Ложь - обновить существующего.
//  ПарольПользователяСервиса - Строка - пароль текущего пользователя
//   для доступа к менеджеру сервиса.
//
Процедура ЗаписатьПользователяСервиса(Знач Пользователь, Знач СоздатьПользователяСервиса, Знач ПарольПользователяСервиса) Экспорт
	
	Если ТипЗнч(Пользователь) = Тип("СправочникСсылка.Пользователи") Тогда
		ПользовательОбъект = Пользователь.ПолучитьОбъект();
	Иначе
		ПользовательОбъект = Пользователь;
	КонецЕсли;
	
	УстановитьПривилегированныйРежим(Истина);
	Прокси = РаботаВМоделиСервиса.ПолучитьПроксиМенеджераСервиса(ПарольПользователяСервиса);
	УстановитьПривилегированныйРежим(Ложь);
	
	Если ЗначениеЗаполнено(ПользовательОбъект.ИдентификаторПользователяИБ) Тогда
		ПользовательИБ = ПользователиИнформационнойБазы.НайтиПоУникальномуИдентификатору(ПользовательОбъект.ИдентификаторПользователяИБ);
		ДоступРазрешен = ПользовательИБ <> Неопределено И Пользователи.ВходВПрограммуРазрешен(ПользовательИБ);
	Иначе
		ДоступРазрешен = Ложь;
	КонецЕсли;
	
	ПользовательСервиса = Прокси.ФабрикаXDTO.Создать(
		Прокси.ФабрикаXDTO.Тип("http://www.1c.ru/SaaS/ApplicationUsers", "User"));
	ПользовательСервиса.Zone = РаботаВМоделиСервиса.ЗначениеРазделителяСеанса();
	ПользовательСервиса.UserServiceID = ПользовательОбъект.ИдентификаторПользователяСервиса;
	ПользовательСервиса.FullName = ПользовательОбъект.Наименование;
	ПользовательСервиса.Name = ПользовательИБ.Имя;
	ПользовательСервиса.StoredPasswordValue = ПользовательИБ.СохраняемоеЗначениеПароля;
	ПользовательСервиса.Language = ПолучитьКодЯзыка(ПользовательИБ.Язык);
	ПользовательСервиса.Access = ДоступРазрешен;
	ПользовательСервиса.AdmininstrativeAccess = ДоступРазрешен И ПользовательИБ.Роли.Содержит(Метаданные.Роли.ПолныеПрава);
	
	КонтактнаяИнформация = Прокси.ФабрикаXDTO.Создать(
		Прокси.ФабрикаXDTO.Тип("http://www.1c.ru/SaaS/ApplicationUsers", "ContactsList"));
		
	ТипЗаписьКИ = Прокси.ФабрикаXDTO.Тип("http://www.1c.ru/SaaS/ApplicationUsers", "ContactsItem");
	
	Для каждого СтрокаКИ Из ПользовательОбъект.КонтактнаяИнформация Цикл
		ВидКИXDTO = РаботаВМоделиСервисаПовтИсп.СоответствиеВидовКИПользователяXDTO().Получить(СтрокаКИ.Вид);
		Если ВидКИXDTO = Неопределено Тогда
			Продолжить;
		КонецЕсли;
		
		ЗаписьКИ = Прокси.ФабрикаXDTO.Создать(ТипЗаписьКИ);
		ЗаписьКИ.ContactType = ВидКИXDTO;
		ЗаписьКИ.Value = СтрокаКИ.Представление;
		ЗаписьКИ.Parts = СтрокаКИ.ЗначенияПолей;
		
		КонтактнаяИнформация.Item.Добавить(ЗаписьКИ);
	КонецЦикла;
	
	ПользовательСервиса.Contacts = КонтактнаяИнформация;
	
	ИнформацияОбОшибке = Неопределено;
	Если СоздатьПользователяСервиса Тогда
		Прокси.CreateUser(ПользовательСервиса, ИнформацияОбОшибке);
		ОбработатьИнформациюОбОшибкеWebСервиса(ИнформацияОбОшибке, "CreateUser"); // Имя операции не локализуется.
	Иначе
		Прокси.UpdateUser(ПользовательСервиса, ИнформацияОбОшибке);
		ОбработатьИнформациюОбОшибкеWebСервиса(ИнформацияОбОшибке, "UpdateUser"); // Имя операции не локализуется.
	КонецЕсли;
	
КонецПроцедуры

////////////////////////////////////////////////////////////////////////////////
// Обработка пользователя ИБ в ходе записи элемента справочника Пользователи и ВнешниеПользователи.

// Вызывается из процедуры НачатьОбработкуПользователяИБ для поддержки модели сервиса.
Процедура ПередНачаломОбработкиПользователяИБ(ПользовательОбъект, ПараметрыОбработки) Экспорт
	
	Если Не ОбщегоНазначенияПовтИсп.РазделениеВключено() Тогда
		Возврат;
	КонецЕсли;
	
	ДополнительныеСвойства = ПользовательОбъект.ДополнительныеСвойства;
	СтарыйПользователь     = ПараметрыОбработки.СтарыйПользователь;
	АвтоРеквизиты          = ПараметрыОбработки.АвтоРеквизиты;
	
	Если ТипЗнч(ПользовательОбъект) = Тип("СправочникОбъект.ВнешниеПользователи")
	   И ОбщегоНазначенияПовтИсп.РазделениеВключено() Тогда
		
		ВызватьИсключение НСтр("ru = 'Внешние пользователи не поддерживаются в модели сервиса.'");
	КонецЕсли;
	
	АвтоРеквизиты.Вставить("ИдентификаторПользователяСервиса", СтарыйПользователь.ИдентификаторПользователяСервиса);
	
	Если ДополнительныеСвойства.Свойство("ОбработкаСообщенияКаналаУдаленногоАдминистрирования") Тогда
		
		Если НЕ ОбщегоНазначенияПовтИсп.СеансЗапущенБезРазделителей() Тогда
			ВызватьИсключение
				НСтр("ru = 'Обновление пользователя по сообщению
				           |канала удаленного администрирования
				           |доступно только неразделенным пользователям.'");
		КонецЕсли;
		
		ПараметрыОбработки.Вставить("ОбработкаСообщенияКаналаУдаленногоАдминистрирования");
		АвтоРеквизиты.ИдентификаторПользователяСервиса = ПользовательОбъект.ИдентификаторПользователяСервиса;
		
	ИначеЕсли НЕ ПользовательОбъект.Служебный Тогда
		ОбновитьОписаниеWebСервисаМенеджераСервиса();
	КонецЕсли;
	
	Если ЗначениеЗаполнено(АвтоРеквизиты.ИдентификаторПользователяСервиса)
	   И АвтоРеквизиты.ИдентификаторПользователяСервиса <> СтарыйПользователь.ИдентификаторПользователяСервиса Тогда
		
		Если ЗначениеЗаполнено(СтарыйПользователь.ИдентификаторПользователяСервиса) Тогда
			
			ВызватьИсключение СтроковыеФункцииКлиентСервер.ПодставитьПараметрыВСтроку(
				НСтр("ru = 'Ошибка при записи пользователя ""%1"".
				           |Нельзя изменять уже установленный идентификатор
				           |пользователя сервиса в элементе справочника.'"),
				ПользовательОбъект.Наименование);
			
		КонецЕсли;
		
		НайденныйПользователь = Неопределено;
		
		Если ПользователиСлужебный.ПользовательПоИдентификаторуСуществует(
				АвтоРеквизиты.ИдентификаторПользователяСервиса,
				ПользовательОбъект.Ссылка,
				НайденныйПользователь,
				Истина) Тогда
			
			ВызватьИсключение СтроковыеФункцииКлиентСервер.ПодставитьПараметрыВСтроку(
				НСтр("ru = 'Ошибка при записи пользователя ""%1"".
				           |Нельзя устанавливать идентификатор
				           |пользователя сервиса ""%2""
				           |в этот элемент справочника, т.к. он
				           |уже используется в элементе ""%3"".'"),
				ПользовательОбъект.Наименование,
				АвтоРеквизиты.ИдентификаторПользователяСервиса,
				НайденныйПользователь);
		КонецЕсли;
	КонецЕсли;
	
КонецПроцедуры

// Вызывается из процедуры НачатьОбработкуПользователяИБ для поддержки модели сервиса.
Процедура ПослеНачалаОбработкиПользователяИБ(ПользовательОбъект, ПараметрыОбработки) Экспорт
	
	Если Не ОбщегоНазначенияПовтИсп.РазделениеВключено() Тогда
		Возврат;
	КонецЕсли;
	
	АвтоРеквизиты = ПараметрыОбработки.АвтоРеквизиты;
	
	ПараметрыОбработки.Вставить("СоздатьПользователяСервиса", Ложь);
	
	Если ПараметрыОбработки.НовыйПользовательИБСуществует
	   И ОбщегоНазначенияПовтИсп.РазделениеВключено() Тогда
		
		Если НЕ ЗначениеЗаполнено(АвтоРеквизиты.ИдентификаторПользователяСервиса) Тогда
			
			ПараметрыОбработки.Вставить("СоздатьПользователяСервиса", Истина);
			ПользовательОбъект.ИдентификаторПользователяСервиса = Новый УникальныйИдентификатор;
			
			// Обновление значения реквизита контролируемого при записи.
			АвтоРеквизиты.ИдентификаторПользователяСервиса = ПользовательОбъект.ИдентификаторПользователяСервиса;
		КонецЕсли;
	КонецЕсли;
	
КонецПроцедуры

// Вызывается из процедуры ЗавершитьОбработкуПользователяИБ для поддержки модели сервиса.
Процедура ПередЗавершениемОбработкиПользователяИБ(ПользовательОбъект, ПараметрыОбработки) Экспорт
	
	Если Не ОбщегоНазначенияПовтИсп.РазделениеВключено() Тогда
		Возврат;
	КонецЕсли;
	
	АвтоРеквизиты = ПараметрыОбработки.АвтоРеквизиты;
	
	Если АвтоРеквизиты.ИдентификаторПользователяСервиса <> ПользовательОбъект.ИдентификаторПользователяСервиса Тогда
		ВызватьИсключение СтроковыеФункцииКлиентСервер.ПодставитьПараметрыВСтроку(
			НСтр("ru = 'Ошибка при записи пользователя ""%1"".
			           |Реквизит ИдентификаторПользователяСервиса не допускается изменять.
			           |Обновление реквизита выполняется автоматически.'"),
			ПользовательОбъект.Ссылка);
	КонецЕсли;
	
КонецПроцедуры

// Вызывается из процедуры ЗавершитьОбработкуПользователяИБ для поддержки модели сервиса.
Процедура ПриЗавершенииОбработкиПользователяИБ(ПользовательОбъект, ПараметрыОбработки, ОбновлятьРоли) Экспорт
	
	Если Не ОбщегоНазначенияПовтИсп.РазделениеВключено() Тогда
		Возврат;
	КонецЕсли;
	
	Если ПараметрыОбработки.Свойство("ОбработкаСообщенияКаналаУдаленногоАдминистрирования") Тогда
		ОбновлятьРоли = Ложь;
	КонецЕсли;
	
	ОписаниеПользователяИБ = ПользовательОбъект.ДополнительныеСвойства.ОписаниеПользователяИБ;
	
	Если ОбщегоНазначенияПовтИсп.РазделениеВключено()
	   И ТипЗнч(ПользовательОбъект) = Тип("СправочникОбъект.Пользователи")
	   И ОписаниеПользователяИБ.Свойство("РезультатДействия")
	   И НЕ ПользовательОбъект.Служебный Тогда
		
		Если ОписаниеПользователяИБ.РезультатДействия = "УдаленПользовательИБ" Тогда
			
			УстановитьПривилегированныйРежим(Истина);
			АннулироватьДоступПользователяСервиса(ПользовательОбъект);
			УстановитьПривилегированныйРежим(Ложь);
			
		Иначе // ДобавленПользовательИБ или ИзмененПользовательИБ.
			ОбновитьПользователяСервиса(ПользовательОбъект, ПараметрыОбработки.СоздатьПользователяСервиса);
		КонецЕсли;
	КонецЕсли;
	
КонецПроцедуры

#КонецОбласти

#Область СлужебныеПроцедурыИФункции

// Для процедуры ПриЗавершенииОбработкиПользователяИБ.
Процедура ОбновитьПользователяСервиса(ПользовательОбъект, СоздатьПользователяСервиса)
	
	Если НЕ ПользовательОбъект.ДополнительныеСвойства.Свойство("СинхронизироватьССервисом")
		ИЛИ НЕ ПользовательОбъект.ДополнительныеСвойства.СинхронизироватьССервисом Тогда
		
		Возврат;
	КонецЕсли;
	
	УстановитьПривилегированныйРежим(Истина);
	
	ЗаписатьПользователяСервиса(ПользовательОбъект, 
		СоздатьПользователяСервиса, 
		ПользовательОбъект.ДополнительныеСвойства.ПарольПользователяСервиса);
	
КонецПроцедуры

// Только для внутреннего использования.
Функция ПолучитьПользователейСервиса(ПарольПользователяСервиса) Экспорт
	
	УстановитьПривилегированныйРежим(Истина);
	Прокси = РаботаВМоделиСервиса.ПолучитьПроксиМенеджераСервиса(ПарольПользователяСервиса);
	УстановитьПривилегированныйРежим(Ложь);
	
	ИнформацияОбОшибке = Неопределено;
	
	Попытка
		
		СписокПользователей = Прокси.GetUsersList(РаботаВМоделиСервиса.ЗначениеРазделителяСеанса(), );
		
	Исключение
		
		ПарольПользователяСервиса = Неопределено;
		ВызватьИсключение;
		
	КонецПопытки;
	
	ОбработатьИнформациюОбОшибкеWebСервиса(ИнформацияОбОшибке, "GetUsersList"); // Имя операции не локализуется.
	
	Результат = Новый ТаблицаЗначений;
	Результат.Колонки.Добавить("Идентификатор", Новый ОписаниеТипов("УникальныйИдентификатор"));
	Результат.Колонки.Добавить("Имя", Новый ОписаниеТипов("Строка", , Новый КвалификаторыСтроки(0, ДопустимаяДлина.Переменная)));
	Результат.Колонки.Добавить("ПолноеИмя", Новый ОписаниеТипов("Строка", , Новый КвалификаторыСтроки(0, ДопустимаяДлина.Переменная)));
	Результат.Колонки.Добавить("Доступ", Новый ОписаниеТипов("Булево"));
	
	Для каждого ИнформацияОПользователе Из СписокПользователей.Item Цикл
		СтрокаПользователя = Результат.Добавить();
		СтрокаПользователя.Идентификатор = ИнформацияОПользователе.UserServiceID;
		СтрокаПользователя.Имя = ИнформацияОПользователе.Name;
		СтрокаПользователя.ПолноеИмя = ИнформацияОПользователе.FullName;
		СтрокаПользователя.Доступ = ИнформацияОПользователе.Access;
	КонецЦикла;
	
	Возврат Результат;
	
КонецФункции

// Только для внутреннего использования.
Процедура ПредоставитьДоступПользователюСервиса(Знач ИдентификаторПользователяСервиса, Знач ПарольПользователяСервиса) Экспорт
	
	УстановитьПривилегированныйРежим(Истина);
	Прокси = РаботаВМоделиСервиса.ПолучитьПроксиМенеджераСервиса(ПарольПользователяСервиса);
	УстановитьПривилегированныйРежим(Ложь);
	
	ИнформацияОбОшибке = Неопределено;
	Прокси.GrantUserAccess(
		ОбщегоНазначения.ЗначениеРазделителяСеанса(),
		ИдентификаторПользователяСервиса, 
		ИнформацияОбОшибке);
	ОбработатьИнформациюОбОшибкеWebСервиса(ИнформацияОбОшибке, "GrantUserAccess"); // Имя операции не локализуется.
	
КонецПроцедуры

// Для процедуры ПриЗавершенииОбработкиПользователяИБ.
Процедура АннулироватьДоступПользователяСервиса(ПользовательОбъект)
	
	Если НЕ ЗначениеЗаполнено(ПользовательОбъект.ИдентификаторПользователяСервиса) Тогда
		Возврат;
	КонецЕсли;
	
	НачатьТранзакцию();
	Попытка
		Сообщение = СообщенияВМоделиСервиса.НовоеСообщение(
			СообщенияУправленияПриложениямиИнтерфейс.СообщениеАннулироватьДоступПользователя());
		
		Сообщение.Body.Zone = ОбщегоНазначения.ЗначениеРазделителяСеанса();
		Сообщение.Body.UserServiceID = ПользовательОбъект.ИдентификаторПользователяСервиса;
		
		СообщенияВМоделиСервиса.ОтправитьСообщение(
			Сообщение,
			РаботаВМоделиСервисаПовтИсп.КонечнаяТочкаМенеджераСервиса());
			
		ЗафиксироватьТранзакцию();
	Исключение
		ОтменитьТранзакцию();
		ВызватьИсключение;
	КонецПопытки;
	
КонецПроцедуры

// Проверяет, что переданный пользователь соответствует существующему пользователю информационной
// базы в текущей области данных.
//
// Параметры:
//  Пользователь - СправочникСсылка.Пользователи;
//
// Возвращаемое значение: Булево.
//
Функция ЭтоСуществующийПользовательТекущейОбластиДанных(Знач Пользователь)
	
	УстановитьПривилегированныйРежим(Истина);
	
	Если ЗначениеЗаполнено(Пользователь) Тогда
		
		Если ЗначениеЗаполнено(Пользователь.ИдентификаторПользователяИБ) Тогда
			
			Если ПользователиИнформационнойБазы.НайтиПоУникальномуИдентификатору(Пользователь.ИдентификаторПользователяИБ) <> Неопределено Тогда
				
				Возврат Истина;
				
			Иначе
				
				Возврат Ложь;
				
			КонецЕсли;
			
		Иначе
			
			Возврат Ложь;
			
		КонецЕсли;
		
	Иначе
		
		Возврат Ложь;
		
	КонецЕсли;
	
КонецФункции

////////////////////////////////////////////////////////////////////////////////
// ВСПОМОГАТЕЛЬНЫЕ ПРОЦЕДУРЫ И ФУНКЦИИ

Функция ИдентификаторСервисаТекущегоПользователя()
	
	Возврат ОбщегоНазначения.ЗначениеРеквизитаОбъекта(Пользователи.ТекущийПользователь(), "ИдентификаторПользователяСервиса");
	
КонецФункции

Функция НовыеДействияСПользователемСервиса()
	
	ДействияСПользователемСервиса = Новый Структура;
	ДействияСПользователемСервиса.Вставить("ИзменениеПароля", Ложь);
	ДействияСПользователемСервиса.Вставить("ИзменениеИмени", Ложь);
	ДействияСПользователемСервиса.Вставить("ИзменениеПолногоИмени", Ложь);
	ДействияСПользователемСервиса.Вставить("ИзменениеДоступа", Ложь);
	ДействияСПользователемСервиса.Вставить("ИзменениеАдминистративногоДоступа", Ложь);
	
	ДействияСКИ = Новый Соответствие;
	Для каждого КлючИЗначение Из РаботаВМоделиСервисаПовтИсп.СоответствиеВидовКИПользователяXDTO() Цикл
		ДействияСКИ.Вставить(КлючИЗначение.Ключ, Новый Структура("Изменение", Ложь));
	КонецЦикла;
	// Ключ - ВидКИ, Значение - Структура с правами.
	ДействияСПользователемСервиса.Вставить("КонтактнаяИнформация", ДействияСКИ);
	
	Возврат ДействияСПользователемСервиса;
	
КонецФункции

Функция ПодготовитьОбъектыДоступаПользователя(Фабрика, Пользователь)
	
	ИнформацияПользователя = Фабрика.Создать(
		Фабрика.Тип("http://www.1c.ru/SaaS/ApplicationAccess", "User"));
	ИнформацияПользователя.Zone = РаботаВМоделиСервиса.ЗначениеРазделителяСеанса();
	ИнформацияПользователя.UserServiceID = ОбщегоНазначения.ЗначениеРеквизитаОбъекта(Пользователь, "ИдентификаторПользователяСервиса");
	
	СписокОбъектов = Фабрика.Создать(
		Фабрика.Тип("http://www.1c.ru/SaaS/ApplicationAccess", "ObjectsList"));
		
	СписокОбъектов.Item.Добавить(ИнформацияПользователя);
	
	ТипКИПользователя = Фабрика.Тип("http://www.1c.ru/SaaS/ApplicationAccess", "UserContact");
	
	Для каждого КлючИЗначение Из РаботаВМоделиСервисаПовтИсп.СоответствиеВидовКИПользователяXDTO() Цикл
		ВидКИ = Фабрика.Создать(ТипКИПользователя);
		ВидКИ.UserServiceID = ОбщегоНазначения.ЗначениеРеквизитаОбъекта(Пользователь, "ИдентификаторПользователяСервиса");
		ВидКИ.ContactType = КлючИЗначение.Значение;
		СписокОбъектов.Item.Добавить(ВидКИ);
	КонецЦикла;
	
	Возврат СписокОбъектов;
	
КонецФункции

Функция ПраваДоступаОбъектовXDTOВДействияСПользователемСервиса(Фабрика, ПраваДоступаОбъектовXDTO)
	
	ТипИнформацияПользователя = Фабрика.Тип("http://www.1c.ru/SaaS/ApplicationAccess", "User");
	ТипКИПользователя = Фабрика.Тип("http://www.1c.ru/SaaS/ApplicationAccess", "UserContact");
	
	ДействияСПользователемСервиса = НовыеДействияСПользователемСервиса();
	ДействияСКИ = ДействияСПользователемСервиса.КонтактнаяИнформация;
	
	Для каждого ПраваДоступаОбъектаXDTO Из ПраваДоступаОбъектовXDTO.Item Цикл
		
		Если ПраваДоступаОбъектаXDTO.Object.Тип() = ТипИнформацияПользователя Тогда
			
			Для каждого ЭлементСпискаПрав Из ПраваДоступаОбъектаXDTO.AccessRights.Item Цикл
				ДействиеСПользователем = РаботаВМоделиСервисаПовтИсп.
					СоответствиеПравXDTOДействиямСПользователемСервиса().Получить(ЭлементСпискаПрав.AccessRight);
				ДействияСПользователемСервиса[ДействиеСПользователем] = Истина;
			КонецЦикла;
			
		ИначеЕсли ПраваДоступаОбъектаXDTO.Object.Тип() = ТипКИПользователя Тогда
			ВидКИ = РаботаВМоделиСервисаПовтИсп.СоответствиеВидовКИXDTOВидамКИПользователя().Получить(
				ПраваДоступаОбъектаXDTO.Object.ContactType);
			Если ВидКИ = Неопределено Тогда
				ШаблонСообщения = НСтр("ru = 'Получен неизвестный вид контактной информации: %1'");
				ТекстСообщения = СтроковыеФункцииКлиентСервер.ПодставитьПараметрыВСтроку(ШаблонСообщения, ПраваДоступаОбъектаXDTO.Object.ContactType);
				ВызватьИсключение(ТекстСообщения);
			КонецЕсли;
			
			ДействияСВидомКИ = ДействияСКИ[ВидКИ];
			
			Для каждого ЭлементСпискаПрав Из ПраваДоступаОбъектаXDTO.AccessRights.Item Цикл
				Если ЭлементСпискаПрав.AccessRight = "Change" Тогда
					ДействияСВидомКИ.Изменение = Истина;
				КонецЕсли;
			КонецЦикла;
		Иначе
			ШаблонСообщения = НСтр("ru = 'Получен неизвестный тип объектов доступа: %1'");
			ТекстСообщения = СтроковыеФункцииКлиентСервер.ПодставитьПараметрыВСтроку(ШаблонСообщения, ОбщегоНазначения.ПредставлениеТипаXDTO(ПраваДоступаОбъектаXDTO.Object.Тип()));
			ВызватьИсключение(ТекстСообщения);
		КонецЕсли;
		
	КонецЦикла;
	
	Возврат ДействияСПользователемСервиса;
	
КонецФункции

Функция ПолучитьКодЯзыка(Знач Язык)
	
	Если Язык = Неопределено Тогда
		Возврат "";
	Иначе
		Возврат Язык.КодЯзыка;
	КонецЕсли;
	
КонецФункции

// Обрабатывает информация об ошибке полученную из web-сервиса.
// В случае если передана не пустая информация об ошибке, записывает
// подробное представление ошибки в журнал регистрации и вызывает
// исключение с текстом краткого представления об ошибке.
//
Процедура ОбработатьИнформациюОбОшибкеWebСервиса(Знач ИнформацияОбОшибке, Знач ИмяОперации)
	
	РаботаВМоделиСервиса.ОбработатьИнформациюОбОшибкеWebСервиса(
		ИнформацияОбОшибке,
		ПользователиСлужебныйВМоделиСервисаПовтИсп.ИмяПодсистемыДляСобытийЖурналаРегистрации(),
		"ManageApplication", // Не локализуется
		ИмяОперации);
	
КонецПроцедуры

#КонецОбласти
