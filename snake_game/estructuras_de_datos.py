from enum import Enum

# --- ESTRUCTURAS DE DATOS (Lista Doblemente Enlazada) ---

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None

class DoublyLinkedList:
    """
    Implementación manual de Deque para la serpiente.
    """
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def push_front(self, data):
        """Agrega a la cabeza (Nuevo movimiento)"""
        new_node = Node(data)
        if self.size == 0:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self.size += 1

    def pop_back(self):
        """Elimina de la cola (Movimiento sin crecer)"""
        if self.size == 0: return None
        data = self.tail.data
        if self.size == 1:
            self.head = self.tail = None
        else:
            self.tail = self.tail.prev
            self.tail.next = None
        self.size -= 1
        return data

    def get_head_data(self):
        return self.head.data if self.head else None

class FoodType(Enum):
    APPLE = 1; BLUE_APPLE = 2; PURPLE_APPLE = 3
    LEMON = 4; BERRY = 5; BOMB = 6

FOOD_DESC = {
    FoodType.APPLE: "Crecimiento +1",
    FoodType.BLUE_APPLE: "Crecimiento +2",
    FoodType.PURPLE_APPLE: "Crecimiento +5",
    FoodType.LEMON: "Adelgaza -3",
    FoodType.BERRY: "Tamaño Mínimo",
    FoodType.BOMB: "Muerte Instantánea"
}


