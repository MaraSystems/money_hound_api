from fastapi import HTTPException, status
from pymongo.database import Database
from redis.asyncio import Redis

from src.domains.simulation_accounts.model import SimulationAccount
from src.domains.simulation_transactions.analyze_transaction import analyze_transaction
from src.domains.simulation_transactions.get_simulation_transaction import get_simulation_transaction
from src.domains.simulation_transactions.model import CreateSimulationTransaction, InitiateSimulationTransaction, SimulationTransaction


async def debit_account(holder_account: SimulationAccount, related_account: SimulationAccount, payload: InitiateSimulationTransaction, reference: str, db: Database, cache: Redis):
    simulation_transaction_collection = db.simulation_transactions
    simulation_account_collection = db.simulation_accounts

    balance = holder_account['balance'] - payload.amount
    if balance < 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Insufficient Fund: {holder_account['account_no']}_{holder_account['bank_name']}")

    data = payload.model_dump(exclude=['holder', 'holder_bank', 'related', 'related_bank', 'type', 'category'])
    transaction = CreateSimulationTransaction(
        **data,
        holder=holder_account['account_no'],
        holder_bank=holder_account['bank_name'],
        related=related_account['account_no'],
        related_bank=related_account['bank_name'],
        balance=balance,
        type='DEBIT',
        category='WITHDRAWAL' if payload.category in ['DEPOSIT', 'WITHDRAWAL'] else payload.category,
        status='SUCCESS',
        reported=False,
        reference=reference
    )

    analyzed = await analyze_transaction(transaction, db)
    if analyzed['fraud']:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Unusual Transaction Detected, Fraud Score: {analyzed['fraud_score']}")

    insert = await simulation_transaction_collection.insert_one(transaction.model_dump())
    await simulation_account_collection.update_one({'account_no': holder_account['account_no'], 'bank_name': holder_account['bank_name']}, {'$set': {'balance': balance}})

    inserted_transaction = await get_simulation_transaction(insert.inserted_id, db, cache)
    return inserted_transaction.data


async def credit_account(holder_account: SimulationAccount, related_account: SimulationAccount, payload: InitiateSimulationTransaction, reference: str, db: Database, cache: Redis):
    simulation_transaction_collection = db.simulation_transactions
    simulation_account_collection = db.simulation_accounts

    balance = holder_account['balance'] + payload.amount
    data = payload.model_dump(exclude=['holder', 'holder_bank', 'related', 'related_bank', 'type', 'category'])
    transaction = CreateSimulationTransaction(
        **data,
        holder=holder_account['account_no'],
        holder_bank=holder_account['bank_name'],
        related=related_account['account_no'],
        related_bank=related_account['bank_name'],
        balance=balance,
        type='CREDIT',
        category='DEPOSIT' if payload.category in ['DEPOSIT', 'WITHDRAWAL'] else payload.category,
        status='SUCCESS',
        reported=False,
        reference=reference
    )

    insert = await simulation_transaction_collection.insert_one(transaction.model_dump())
    await simulation_account_collection.update_one({'account_no': holder_account['account_no'], 'bank_name': holder_account['bank_name']}, {'$set': {'balance': balance}})

    inserted_transaction = await get_simulation_transaction(insert.inserted_id, db, cache)
    return inserted_transaction.data
