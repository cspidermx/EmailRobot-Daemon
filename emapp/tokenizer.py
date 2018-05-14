from emapp import logger


def __apnd (txt, frst, scnd, epty, start):
    idx = txt.find(frst, start) + len(frst)
    idx2 = 0
    val = epty
    if idx != -1:
        idx2 = txt.find(scnd, idx)
        if idx2 != -1:
            val = txt[idx:idx2].replace('\\r\\n', '\r\n')
            val = val.replace('\\n', '')
            val = val.strip()
        else:
            idx2 = 0
    return val, idx2


def __score(txt, what, ind):
    idx = txt.find(what, ind)
    if idx != -1:
        return 1, idx
    else:
        return 0, 0


def tkformat(texto):
    score = 0
    s, idx = __score(texto, "Alert Details", 0)
    score += s
    s, idx = __score(texto, "Start Date Time", idx)
    score += s
    s, idx = __score(texto, "End Date Time", idx)
    score += s
    s, idx = __score(texto, "Managed Object", idx)
    score += s
    s, idx = __score(texto, "Category", idx)
    score += s
    s, idx = __score(texto, "Rating", idx)
    score += s
    s, idx = __score(texto, "Status", idx)
    score += s
    s, idx = __score(texto, "Measured Metrics", idx)
    score += s
    s, idx = __score(texto, "Alert Description", idx)
    score += s
    s, idx = __score(texto, "Analysis Tools:", idx)
    score += s
    if score >= 5:
        return 1
    else:
        return 2


def tknzr (texto):
    tk = []
    try:
        resp, idx2 = __apnd(texto, "Alert Details", "Start Date Time", "Sin Detalles", 0)
        tk.append(resp)
        resp, idx2 = __apnd(texto, "Start Date Time", "End Date Time", "Sin fecha/hora de inicio", idx2)
        tk.append(resp)
        resp, idx2 = __apnd(texto, "End Date Time", "Managed Object", "Sin fecha/hora de finalización", idx2)
        tk.append(resp)
        resp, idx2 = __apnd(texto, "Managed Object", "System Login", "Sin Objeto Manejado", idx2)
        tk.append(resp)
        resp, idx2 = __apnd(texto, "Category", "Rating", "Sin Categoría", idx2)
        tk.append(resp)
        resp, idx2 = __apnd(texto, "Rating", "Status", "Sin Valuación", idx2)
        tk.append(resp)
        resp, idx3 = __apnd(texto, "Status", "Measured Metrics", "Sin Estado", idx2)
        if resp.find("Alert Description") != -1:
            resp, idx2 = __apnd(texto, "Status", "Alert Description", "Sin Estado", idx2)
            tk.append(resp)
            resp, idx3 = __apnd(texto, "Description:", "Measured Metrics", "Sin Descripcion", idx2)
            if resp.find("Analysis Tools:") != -1:
                resp, idx2 = __apnd(texto, "Description:", "Analysis Tools:", "Sin Descripcion", idx2)
                tk.append(resp)
                resp, idx2 = __apnd(texto, "Analysis Tools:", "Measured Metrics", "Sin Analisis", idx2)
                tk.append(resp)
            else:
                tk.append(resp)
                tk.append("Sin Analisis")
        else:
            if resp.find("Analysis Tools:") != -1:
                tk.append("Sin Descripcion")
                resp, idx2 = __apnd(texto, "Analysis Tools:", "Measured Metrics", "Sin Descripcion", idx2)
                tk.append(resp)
            else:
                tk.append(resp)
                tk.append("Sin Descripcion")
                tk.append("Sin Analisis")

    except AttributeError:
        tk.append(("Exception", "Not Found"))
        logger.warning("No se encontró algún attributo: {}".format(AttributeError))

    return tk
