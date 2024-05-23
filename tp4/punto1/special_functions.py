def binary_search(arr, x):
        """
        Realiza una búsqueda binaria en un array ordenado.
        Args:
        arr (list): El array ordenado donde se realizará la búsqueda.
        x: El elemento a buscar en el array.
        Returns:
        int: La posición del elemento en el array si se encuentra, -1 si no se encuentra.
        """
        left = 0
        right = len(arr) - 1

        while left <= right:
            mid = (left + right) // 2

            # Si el elemento está en el medio
            if arr[mid] == x:
                return mid
            # Si el elemento es mayor que el valor medio, se busca en la mitad derecha
            elif arr[mid] < x:
                left = mid + 1
            # Si el elemento es menor que el valor medio, se busca en la mitad izquierda
            else:
                right = mid - 1

        # Si el elemento no está en el array
        return -1

