# RACING WHEEL BUTTONS
Racing Wheel Buttons was created to provide a easy way to setting up ESP32 as a push button controller inside an Racing Wheel.

## ESP32
ESP32 Devkit V1 was used to run compiled code, this project **esp-gpio-serial-handler** run through RTOS ESP-IDF framework with a event guided workflow.
### GPIO
First of all, you need to configure gpio as input, pulled up (receives GND), and a kind of interrupt edge, my choise was rising edge. Before this, you also need to setting up what GPIO pins will be used, for a first example, let's setting up 4 GPIO as INPUT:
```C
#define GPIO_INPUT_IO_0     14
#define GPIO_INPUT_IO_1     27
#define GPIO_INPUT_IO_2     26
#define GPIO_INPUT_IO_3     25
#define GPIO_INPUT_PIN_SEL  ((1ULL<<GPIO_INPUT_IO_0) | (1ULL<<GPIO_INPUT_IO_1) | (1ULL<<GPIO_INPUT_IO_2) | (1ULL<<GPIO_INPUT_IO_3))
```

After this, you have to configurate GPIO with ```gpio_config_t``` structure:
```C
//zero-initialize the config structure.
gpio_config_t io_conf = {};
//interrupt of rising edge
io_conf.intr_type = GPIO_INTR_POSEDGE;
//bit mask of the pins, use GPIO4/5 here
io_conf.pin_bit_mask = GPIO_INPUT_PIN_SEL;
//set as input mode
io_conf.mode = GPIO_MODE_INPUT;
//enable pull-up mode
io_conf.pull_up_en = GPIO_PULLUP_ENABLE;
gpio_config(&io_conf);
```

Than you will create a event queue to handle with all gpio events and than add handlers to each GPIO INPUT:
```C
//create a queue to handle gpio event from isr
gpio_evt_queue = xQueueCreate(10, sizeof(uint32_t));
//start gpio task
xTaskCreate(gpio_task_example, "gpio_task_example", 2048, NULL, 10, NULL);

//install gpio isr service
gpio_install_isr_service(ESP_INTR_FLAG_DEFAULT);
//hook isr handler for specific gpio pin
gpio_isr_handler_add(GPIO_INPUT_IO_0, gpio_isr_handler, (void*) GPIO_INPUT_IO_0);
//hook isr handler for specific gpio pin
gpio_isr_handler_add(GPIO_INPUT_IO_1, gpio_isr_handler, (void*) GPIO_INPUT_IO_1);
//hook isr handler for specific gpio pin
gpio_isr_handler_add(GPIO_INPUT_IO_2, gpio_isr_handler, (void*) GPIO_INPUT_IO_2);
//hook isr handler for specific gpio pin
gpio_isr_handler_add(GPIO_INPUT_IO_3, gpio_isr_handler, (void*) GPIO_INPUT_IO_3);
```

Font:
[ESP-IDF Peripherals: GPIO (Generic GPIO)](https://github.com/espressif/esp-idf/blob/54544998776b825cf847d72ad45243f051fd5708/examples/peripherals/gpio/generic_gpio/main/gpio_example_main.c)

### UART
Font:
[ESP-IDF Peripherals: UART (UART ECHO)](https://github.com/espressif/esp-idf/blob/722fde218d20bec4a0c33c613974e1f9de992765/examples/peripherals/uart/uart_echo/main/uart_echo_example_main.c)

## Python